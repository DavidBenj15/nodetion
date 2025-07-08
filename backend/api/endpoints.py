from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import asyncio
from services.chroma import test_upsert, test_get, search_documents
from seed_database import seed_database, clear_database
from services.notion import process_page, process_page_and_insert_to_chromadb

app = FastAPI()

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class ProcessPageRequest(BaseModel):
    page_id: str

@app.post("/")
def post_root():
    return test_upsert()

@app.get("/")
def get_root():
    return test_get()

@app.post("/search")
def search_documents_endpoint(request: SearchRequest):
    """
    Search for documents in ChromaDB based on a user query.
    
    Args:
        request: SearchRequest containing query and optional top_k parameter
    
    Returns:
        JSON response with matching documents and metadata
    """
    return search_documents(request.query, request.top_k)

@app.post("/seed")
def seed_database_endpoint():
    """
    Seed the database with 100 diverse documents for testing
    """
    return seed_database()

@app.delete("/clear")
def clear_database_endpoint():
    """
    Clear all documents from the database (use with caution!)
    """
    return clear_database()

@app.post("/process-notion-page")
async def process_notion_page_endpoint(request: ProcessPageRequest):
    """
    Process a Notion page with the given ID and extract all content chunks.
    
    Args:
        request: ProcessPageRequest containing the Notion page ID
    
    Returns:
        JSON response with processing status and extracted chunks
    """
    try:
        # Initialize empty titles stack for the page hierarchy
        titles_stack = []
        
        # Process the page asynchronously
        await process_page(request.page_id, titles_stack)
        
        return {
            "success": True,
            "message": f"Successfully processed Notion page {request.page_id}",
            "page_id": request.page_id,
            "note": "Check the console/logs for detailed chunk information"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing Notion page {request.page_id}: {str(e)}",
            "page_id": request.page_id,
            "error": str(e)
        }

@app.post("/process-and-insert-notion-page")
async def process_and_insert_notion_page_endpoint(request: ProcessPageRequest):
    """
    Process a Notion page with the given ID and insert all chunks into ChromaDB.
    
    Args:
        request: ProcessPageRequest containing the Notion page ID
    
    Returns:
        JSON response with processing and insertion results
    """
    try:
        # Process the page and insert chunks into ChromaDB
        result = await process_page_and_insert_to_chromadb(request.page_id)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing and inserting Notion page {request.page_id}: {str(e)}",
            "page_id": request.page_id,
            "error": str(e)
        }