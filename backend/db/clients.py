import chromadb
import os
from dotenv import load_dotenv
import logging # For logging tokenizer loading
from transformers import AutoTokenizer # Assuming HuggingFace tokenizer

logger = logging.getLogger(__name__) # Get logger for this module

# Load environment variables
load_dotenv()

# --- ChromaDB Client ---
CHROMADB_HOST = os.getenv("CHROMADB_HOST", "localhost")
CHROMADB_PORT = int(os.getenv("CHROMADB_PORT", 8000))
chroma_client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)

try:
    chroma_client.heartbeat()
    logger.info(f"Connected to ChromaDB at {CHROMADB_HOST}:{CHROMADB_PORT}")
except Exception as e:
    logger.error(f"ERROR: Could not connect to ChromaDB at {CHROMADB_HOST}:{CHROMADB_PORT}. Is Docker running? {e}", exc_info=True)
    # Consider raising here or having a robust retry mechanism

# --- Embedding Model Tokenizer ---
# Define your embedding model's name (e.g., from Sentence Transformers)
# Ensure this matches the model ChromaDB is configured to use for embeddings!
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

try:
    logger.info(f"Loading tokenizer for embedding model: {EMBEDDING_MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL_NAME)
    logger.info("Tokenizer loaded successfully.")
except Exception as e:
    logger.critical(f"ERROR: Could not load tokenizer for model {EMBEDDING_MODEL_NAME}: {e}", exc_info=True)
    # If the tokenizer fails to load, your embedding process is broken.
    # It's often appropriate to exit here, or at least raise a critical error.
    # sys.exit(1) # Uncomment if you want to exit immediately on this failure