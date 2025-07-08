import httpx
import asyncio
import os
import json
import sys
import logging
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Any, Optional
from pprint import pprint
# from transformers import AutoTokenizer

# --- 1. Centralized Logging (Best Practice) ---
logging.basicConfig(
    level=logging.INFO, # Changed to INFO for general messages
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# For errors that print traceback:
logger = logging.getLogger(__name__)

load_dotenv()

NOTION_CONFIG = {
    "base_url": os.getenv("NOTION_BASE"),
    "secret": os.getenv("NOTION_SECRET"),
    "version": os.getenv("NOTION_VERSION")
}

# Validate essential environment variables
if not all(NOTION_CONFIG.values()):
    logger.critical("Missing one or more Notion environment variables (NOTION_BASE, NOTION_SECRET, NOTION_VERSION). Exiting.")
    sys.exit(1)

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_CONFIG['secret']}",
    "Notion-Version": NOTION_CONFIG['version']
}

# Block types that we can easily extract text from
STRING_BLOCK_TYPES = {
    'bulleted_list_item', 'child_page', 'code', 'embed', 'link_preview',
    'numbered_list_item', 'paragraph', 'quote', 'to_do', 'toggle',
    'heading_1', 'heading_2', 'heading_3'
}

HEADING_TYPES = {'heading_1', 'heading_2', 'heading_3'}

# --- ASYNC FUNCTIONS ---

async def fetch_url(url: str, headers: Optional[Dict[str, str]] = None) -> httpx.Response:
    """Fetches a URL asynchronously and raises an exception for bad status codes."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
            return response
    except httpx.RequestError as exc:
        logger.error(f"HTTPX Request Error for {url}: {exc}", exc_info=True)
        raise # Re-raise to be handled by calling function
    except httpx.HTTPStatusError as exc:
        logger.error(f"HTTP Error {exc.response.status_code} for {url}: {exc.response.text}", exc_info=True)
        raise # Re-raise to be handled by calling function

def get_title(page_json: Dict) -> str:
    """Extracts the plain text title from a Notion page JSON."""
    try:
        # Notion titles are lists of rich_text objects, so access [0]['plain_text']
        return page_json['properties']['title']['title'][0]['plain_text']
    except (KeyError, IndexError, TypeError):
        logger.warning(f"Could not extract title from page JSON: {json.dumps(page_json, indent=2)}")
        return ""

async def get_block_contents(block_id: str) -> Tuple[List[Tuple[Optional[str], str, str]], List[str]]:
    """
    Recursively fetches block contents and subpage IDs.
    Returns (list of (text, type, updated_at) tuples, list of subpage_ids).
    """
    all_blocks_data = [] # Stores (text_content, block_type, updated_at)
    current_subpage_ids = []

    try:
        block_res = await fetch_url(f"{NOTION_CONFIG['base_url']}/v1/blocks/{block_id}/children", NOTION_HEADERS)
        block_json = block_res.json()

        for block in block_json['results']:
            block_type = block["type"]
            block_id_current = block["id"] # Use a distinct variable name
            
            # Extract updated_at timestamp
            updated_at = block.get("last_edited_time", "")

            if block_type == "child_page":
                all_blocks_data.append((block_id_current, block_type, updated_at)) # Store ID for child_page
                current_subpage_ids.append(block_id_current)
                continue
            elif block_type in STRING_BLOCK_TYPES:
                try:
                    # Access text content for various block types
                    text_content = ""
                    if 'rich_text' in block[block_type] and block[block_type]['rich_text']:
                        text_content = block[block_type]['rich_text'][0]['plain_text']
                    elif block_type == 'code' and 'caption' in block['code']: # Special handling for code captions
                         text_content = block['code']['rich_text'][0]['plain_text']
                    elif block_type == 'link_preview' and 'url' in block['link_preview']:
                        text_content = block['link_preview']['url'] # Get URL for link_preview
                    
                    all_blocks_data.append((text_content, block_type, updated_at))

                except (KeyError, IndexError, TypeError) as e:
                    # Log the problematic block JSON and error, then continue instead of exiting
                    logger.error(
                        f"Error extracting text from block type '{block_type}' (ID: {block_id_current}): {e}\n"
                        f"Problematic block JSON: {json.dumps(block, indent=2)}",
                        exc_info=True # Includes traceback
                    )
                    all_blocks_data.append(("", block_type, updated_at)) # Append empty string to maintain structure
                    continue # Continue processing other blocks

                if block.get("has_children", False): # Safely check for 'has_children'
                    # Recursively get children blocks and extend the lists
                    child_blocks_data, child_subpage_ids = await get_block_contents(block_id_current)
                    all_blocks_data.extend(child_blocks_data)
                    current_subpage_ids.extend(child_subpage_ids)

    except Exception as e:
        logger.error(f"Error processing block children for {block_id}: {e}", exc_info=True)
        raise # Re-raise if a fundamental fetch error occurred

    return all_blocks_data, current_subpage_ids


def split_text_by_tokens(text: str, tokenizer: Any, max_tokens: int, overlap_tokens: int) -> List[str]:
    chunks = []
    return chunks

def get_most_recent_timestamp(timestamps: List[str]) -> str:
    """
    Find the most recent timestamp from a list of ISO 8601 timestamps.
    Returns the most recent timestamp, or empty string if no valid timestamps.
    """
    if not timestamps:
        return ""
    
    # Filter out empty timestamps
    valid_timestamps = [ts for ts in timestamps if ts]
    if not valid_timestamps:
        return ""
    
    try:
        # Parse timestamps and find the most recent one
        from datetime import datetime
        parsed_timestamps = []
        for ts in valid_timestamps:
            try:
                # Parse ISO 8601 timestamp
                parsed = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                parsed_timestamps.append((parsed, ts))
            except ValueError:
                logger.warning(f"Invalid timestamp format: {ts}")
                continue
        
        if parsed_timestamps:
            # Sort by parsed datetime and return the most recent original timestamp
            parsed_timestamps.sort(key=lambda x: x[0], reverse=True)
            return parsed_timestamps[0][1]
        
    except Exception as e:
        logger.error(f"Error parsing timestamps: {e}")
    
    return ""

# Redefine apply_hierarchy to yield chunks with context and metadata
def apply_hierarchy_and_chunk(
    blocks_data: List[Tuple[Optional[str], str, str]],
    ancestor_titles: List[str], # Renamed for clarity to reflect all page ancestors
    page_id: str # Pass the current page ID for metadata
) -> List[Dict[str, Any]]:
    """
    Applies hierarchical context to block contents and generates structured chunks.
    Yields dictionaries, each representing a chunk ready for embedding.
    """
    heading_level_map = {
        'heading_1': 1,
        'heading_2': 2,
        'heading_3': 3
    }
    
    current_headings = [None, None, None] # Stores the text of the active headings
    current_heading_types = [None, None, None] # Stores the types of active headings
    
    chunks_for_page = []
    
    for i, (content, block_type, updated_at) in enumerate(blocks_data):
        # Track headings for markdown formatting
        if block_type in HEADING_TYPES:
            idx = heading_level_map[block_type] - 1  # Convert to 0-based index
            current_headings[idx] = content
            current_heading_types[idx] = block_type
            for j in range(idx + 1, len(current_headings)):
                current_headings[j] = None
                current_heading_types[j] = None
        
        # Prepare the core content for the chunk with markdown formatting
        core_content = None
        if block_type == 'paragraph':
            core_content = content
        elif block_type == 'bulleted_list_item':
            core_content = f"- {content}"
        elif block_type == 'numbered_list_item':
            core_content = f"1. {content}"  # Note: ChromaDB doesn't maintain list order, so we use 1.
        elif block_type == 'code':
            core_content = f"```\n{content}\n```"
        elif block_type == 'quote':
            core_content = f"> {content}"
        elif block_type == 'to_do':
            # TODO: Add checkbox state from Notion API if available
            core_content = f"- [ ] {content}"
        elif block_type == 'toggle':
            core_content = f"<details>\n<summary>{content}</summary>\n</details>"
        elif block_type == 'link_preview':
            core_content = f"[Link]({content})"
        elif block_type == 'child_page':
            # Child pages are handled by recursive calls to process_page,
            # so they don't produce content chunks here.
            # However, if you wanted a chunk for the *link itself*, you'd handle it here.
            continue # Skip creating a content chunk for the child_page block itself

        if core_content is not None:
            # Build markdown-formatted context
            markdown_context_parts = []
            
            # Add page title hierarchy with markdown formatting
            for title in ancestor_titles:
                if title:  # Only add non-empty titles
                    markdown_context_parts.append(f"# {title}")
            
            # Add active headings with markdown formatting
            for heading_text, heading_type in zip(current_headings, current_heading_types):
                if heading_text and heading_type:
                    level = heading_level_map[heading_type]
                    markdown_prefix = "#" * level
                    markdown_context_parts.append(f"{markdown_prefix} {heading_text}")
            
            # Add the core content
            markdown_context_parts.append(core_content)
            
            # Join with newlines for proper markdown formatting
            full_chunk_text_unsplit = "\n\n".join(filter(None, markdown_context_parts))
            
            # --- Sub-chunking for long texts ---
            # This is a conceptual step. You'll need a proper tokenizer (e.g., from HuggingFace transformers)
            # to count tokens accurately and split intelligently.
            MAX_CHUNK_TOKENS = 256 # Example value
            OVERLAP_TOKENS = 50    # Example value

            # Dummy splitting for illustration - replace with actual tokenization/splitting
            # For simplicity, let's just split by words here
            words = full_chunk_text_unsplit.split()
            
            if len(words) * 1.3 > MAX_CHUNK_TOKENS: # Rough estimate: 1 word ~ 1.3 tokens
                # Implement more sophisticated splitting for very long blocks
                # For now, if it's too long, it might be truncated or split poorly.
                # A proper solution involves iterating, tokenizing, and checking length.
                # Example:
                # from transformers import AutoTokenizer
                # tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
                # tokens = tokenizer.encode(full_chunk_text_unsplit)
                # if len(tokens) > MAX_CHUNK_TOKENS:
                #    ... splitting logic ...
                logger.warning(f"Chunk from page {page_id} (block index {i}) is very long: {len(words)} words. May need splitting.")
                # Fallback: Just use the full text if splitting isn't fully implemented yet
                sub_chunks = [full_chunk_text_unsplit] 
            else:
                sub_chunks = [full_chunk_text_unsplit] # No need to split

            # Collect timestamps from all blocks that contribute to this chunk
            # This includes the current block and any heading blocks that provide context
            chunk_timestamps = [updated_at]  # Start with current block's timestamp
            
            # Add timestamps from heading blocks that provide context
            for j, (heading_content, heading_type, heading_timestamp) in enumerate(blocks_data):
                if heading_type in HEADING_TYPES and heading_content in current_headings:
                    chunk_timestamps.append(heading_timestamp)
            
            # Get the most recent timestamp for this chunk
            most_recent_timestamp = get_most_recent_timestamp(chunk_timestamps)

            # Get active headings for metadata (without markdown formatting)
            active_headings_text = [h for h in current_headings if h is not None]

            for sub_chunk_text in sub_chunks:
                chunks_for_page.append({
                    "id": f"{page_id}-{i}", # Unique ID for each block (or sub-chunk)
                    "text": sub_chunk_text,
                    "source_page_id": page_id,
                    "source_block_id": blocks_data[i][0] if blocks_data[i][1] == 'child_page' else None, # The Notion block ID itself
                    "page_title_path": list(ancestor_titles), # List of page titles in hierarchy
                    "active_headings": active_headings_text, # List of active H1/H2/H3 texts
                    "block_type": block_type,
                    "order_within_page": i, # Maintain original order
                    "last_updated": most_recent_timestamp, # Most recent update timestamp for this chunk
                    # Add other Notion metadata here (e.g., creation date, last edited)
                })
    
    return chunks_for_page

async def process_page(page_id: str, titles_stack: List[str], all_chunks: List[Dict[str, Any]] = None):
    """
    Recursively processes a Notion page, its blocks, and its child pages.
    titles_stack: a list used as a stack to keep track of ancestor page titles.
    all_chunks: optional list to collect all chunks from all pages
    """
    
    # Ensure titles_stack is correctly managed for recursion
    original_titles_stack_len = len(titles_stack)
    
    try:
        # Fetch page details
        page_res = await fetch_url(f"{NOTION_CONFIG['base_url']}/v1/pages/{page_id}", NOTION_HEADERS)
        page_json = page_res.json()
        
        page_title = get_title(page_json)
        titles_stack.append(page_title) # Add current page's title to the stack

        # Get all blocks (including nested ones and child page IDs)
        blocks_data, subpage_ids = await get_block_contents(page_id)
        
        # Process the blocks with the current hierarchy (including this page's title)
        page_chunks = apply_hierarchy_and_chunk(blocks_data, titles_stack, page_id)
        
        # Print processed strings for this page
        pprint(page_chunks)
        
        # Collect chunks if all_chunks list is provided
        if all_chunks is not None:
            all_chunks.extend(page_chunks)

        # Recursively process subpages
        for subpage_id in subpage_ids:
            await process_page(subpage_id, titles_stack, all_chunks)

    except Exception as e:
        logger.error(f"Error processing page {page_id} (title: '{titles_stack[-1] if titles_stack else 'N/A'}'): {e}", exc_info=True)
        # Depending on severity, you might want to re-raise or just log and continue for other pages
    finally:
        # Crucial for managing the `titles_stack` in a recursive context
        # Pop the current page's title off the stack when done with it and its children
        while len(titles_stack) > original_titles_stack_len:
            titles_stack.pop()

async def process_page_and_insert_to_chromadb(page_id: str) -> Dict[str, Any]:
    """
    Process a Notion page and insert all chunks into ChromaDB.
    
    Args:
        page_id: The Notion page ID to process
    
    Returns:
        dict: Response containing processing and insertion results
    """
    try:
        from services.chroma import insert_notion_chunks, delete_chunks_by_page_id
        
        # Initialize collection for all chunks
        all_chunks = []
        titles_stack = []
        
        # Process the page and collect all chunks
        await process_page(page_id, titles_stack, all_chunks)
        
        if not all_chunks:
            return {
                "success": False,
                "message": f"No chunks extracted from page {page_id}",
                "page_id": page_id,
                "chunks_count": 0
            }
        
        # Delete existing chunks for this page (to avoid duplicates)
        # TODO: only update chunk if it contains a page that was updated
        delete_result = delete_chunks_by_page_id(page_id)
        if not delete_result["success"]:
            logger.warning(f"Failed to delete existing chunks for page {page_id}: {delete_result['message']}")
        
        # Insert new chunks into ChromaDB
        insert_result = insert_notion_chunks(all_chunks)
        
        if insert_result["success"]:
            return {
                "success": True,
                "message": f"Successfully processed and inserted {len(all_chunks)} chunks for page {page_id}",
                "page_id": page_id,
                "chunks_count": len(all_chunks),
                "inserted_count": insert_result["inserted_count"],
                "deleted_previous": delete_result.get("deleted_count", 0)
            }
        else:
            return {
                "success": False,
                "message": f"Failed to insert chunks into ChromaDB: {insert_result['message']}",
                "page_id": page_id,
                "chunks_count": len(all_chunks),
                "error": insert_result.get("error", "Unknown error")
            }
            
    except Exception as e:
        logger.error(f"Error processing page {page_id} and inserting to ChromaDB: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error processing page {page_id}: {str(e)}",
            "page_id": page_id,
            "chunks_count": 0,
            "error": str(e)
        }


if __name__ == "__main__":
    # Example usage: Replace with your actual Notion page ID
    initial_page_id = "21d9b1e8c8538094b211d71355b35569"
    
    titles_history = [] # This list acts as the global stack for titles
    
    logger.info(f"Starting Notion page processing for ID: {initial_page_id}")
    try:
        asyncio.run(process_page(initial_page_id, titles_history))
        logger.info("Processing complete.")
    except Exception as e:
        logger.critical(f"Unhandled fatal error during processing: {e}", exc_info=True)