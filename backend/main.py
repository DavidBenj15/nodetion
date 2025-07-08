import uvicorn
from api.endpoints import app

if __name__ == "__main__":
    uvicorn.run(
        "api.endpoints:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    ) 