from db.clients import chroma_client

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
        dict: Response containing success status, message, and search results
    """
    try:
        # Query the collection
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Format the results for better readability
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, (doc, distance, id_val) in enumerate(zip(
                results['documents'][0], 
                results['distances'][0], 
                results['ids'][0]
            )):
                formatted_results.append({
                    "rank": i + 1,
                    "document": doc,
                    "similarity_score": 1 - distance,  # Convert distance to similarity score
                    "id": id_val
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