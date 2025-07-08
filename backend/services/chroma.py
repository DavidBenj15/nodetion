from db.clients import chroma_client
from typing import List, Dict, Any, Optional

collection = chroma_client.get_or_create_collection(name="test_collection")

def test_upsert():
    try:
        collection.upsert(
            documents=[
                "This is a document about hyraxes, and how freaky they are.",
                "This is a document about the city of Baltimore"
            ],
            ids=["id1", "id2"]
        )
        return {
            "success": True,
            "message": "Data upserted successfully."
        }
    except Exception as e:
        return {
            "success": False,
            "message": e
        }
    
def test_get():
    try:
        res = collection.query(
            query_texts=["This is a query about Johns Hopkins University"],
            n_results=1
        )
        return {
            "success": True,
            "message": "Data fetched successfully.",
            "data": res
        }
    except Exception as e:
        return {
            "success": False,
            "message": e
        }

def search_documents(query: str, top_k: int = 5):
    """
    Search for documents in ChromaDB based on a user query.
    
    Args:
        query (str): The user's search query
        top_k (int): Number of top matching documents to return (default: 5)
    
    Returns:
        dict: Response containing success status, message, and search results with metadata
    """
    try:
        # Query the collection with metadata
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["metadatas", "documents", "distances"]
        )
        
        # Format the results for better readability
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, (doc, distance, id_val, metadata) in enumerate(zip(
                results['documents'][0], 
                results['distances'][0], 
                results['ids'][0],
                results['metadatas'][0]
            )):
                # Parse metadata back into structured format
                parsed_metadata = {
                    "source_page_id": metadata.get("source_page_id", ""),
                    "block_type": metadata.get("block_type", ""),
                    "order_within_page": metadata.get("order_within_page", 0),
                    "last_updated": metadata.get("last_updated", ""),
                    "page_title_path": metadata.get("page_title_path", "").split(" > ") if metadata.get("page_title_path") else [],
                    "active_headings": metadata.get("active_headings", "").split(" | ") if metadata.get("active_headings") else [],
                }
                
                # Add optional source_block_id if it exists
                if metadata.get("source_block_id"):
                    parsed_metadata["source_block_id"] = metadata["source_block_id"]
                
                formatted_results.append({
                    "rank": i + 1,
                    "document": doc,
                    "similarity_score": 1 - distance,  # Convert distance to similarity score
                    "id": id_val,
                    "metadata": parsed_metadata
                })
        
        return {
            "success": True,
            "message": f"Found {len(formatted_results)} matching documents",
            "query": query,
            "top_k": top_k,
            "results": formatted_results
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error searching documents: {str(e)}",
            "query": query,
            "top_k": top_k,
            "results": []
        }

def insert_notion_chunks(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Insert Notion chunks into ChromaDB with metadata.
    
    Args:
        chunks: List of chunk dictionaries with text and metadata
    
    Returns:
        dict: Response containing success status and insertion results
    """
    try:
        if not chunks:
            return {
                "success": True,
                "message": "No chunks to insert",
                "inserted_count": 0
            }
        
        # Prepare data for ChromaDB upsert
        documents = []
        ids = []
        metadatas = []
        
        for chunk in chunks:
            # Extract text content
            documents.append(chunk["text"])
            
            # Create unique ID
            chunk_id = chunk["id"]
            ids.append(chunk_id)
            
            # Prepare metadata (ChromaDB metadata must be flat strings/numbers)
            metadata = {
                "source_page_id": chunk["source_page_id"],
                "block_type": chunk["block_type"],
                "order_within_page": chunk["order_within_page"],
                "last_updated": chunk["last_updated"],
                "page_title_path": " > ".join(chunk["page_title_path"]),  # Join as string
                "active_headings": " | ".join(chunk["active_headings"]),  # Join as string
            }
            
            # Add source_block_id if it exists
            if chunk.get("source_block_id"):
                metadata["source_block_id"] = chunk["source_block_id"]
            
            metadatas.append(metadata)
        
        # Insert into ChromaDB
        collection.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        return {
            "success": True,
            "message": f"Successfully inserted {len(chunks)} chunks into ChromaDB",
            "inserted_count": len(chunks),
            "chunk_ids": ids
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error inserting chunks into ChromaDB: {str(e)}",
            "inserted_count": 0,
            "error": str(e)
        }

def get_collection_stats() -> Dict[str, Any]:
    """
    Get statistics about the ChromaDB collection.
    
    Returns:
        dict: Collection statistics
    """
    try:
        count = collection.count()
        return {
            "success": True,
            "total_documents": count,
            "collection_name": collection.name
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting collection stats: {str(e)}",
            "error": str(e)
        }

def delete_chunks_by_page_id(page_id: str) -> Dict[str, Any]:
    """
    Delete all chunks associated with a specific Notion page ID.
    
    Args:
        page_id: The Notion page ID to delete chunks for
    
    Returns:
        dict: Response containing deletion results
    """
    try:
        # Query to find chunks with the specific page_id
        results = collection.query(
            query_texts=[""],  # Empty query to get all documents
            n_results=collection.count(),
            where={"source_page_id": page_id}
        )
        
        if results['ids'] and results['ids'][0]:
            # Delete the found chunks
            collection.delete(ids=results['ids'][0])
            
            return {
                "success": True,
                "message": f"Deleted {len(results['ids'][0])} chunks for page {page_id}",
                "deleted_count": len(results['ids'][0])
            }
        else:
            return {
                "success": True,
                "message": f"No chunks found for page {page_id}",
                "deleted_count": 0
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Error deleting chunks for page {page_id}: {str(e)}",
            "error": str(e)
        }