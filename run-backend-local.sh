#!/bin/bash

# Kill any existing process on port 8001
lsof -ti:8001 | xargs kill -9 2>/dev/null || true

# Run the ChromaDB
docker compose up -d chromadb

# Run the FastAPI app as a daemon
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn api.endpoints:app --reload --host 0.0.0.0 --port 8001
cd ..