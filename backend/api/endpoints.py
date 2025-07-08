from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from services.chroma import test_upsert, test_get, search_documents
from seed_database import seed_database, clear_database

app = FastAPI()

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

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