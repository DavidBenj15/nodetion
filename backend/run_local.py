#!/usr/bin/env python3
"""
Script to run the FastAPI app locally on port 8001
"""
import uvicorn
from api.endpoints import app

if __name__ == "__main__":
    print("Starting FastAPI app on http://localhost:8001")
    print("ChromaDB should be running on http://localhost:8000")
    uvicorn.run(
        "api.endpoints:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 