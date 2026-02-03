import os
import sys


_proxy_vars = [
    'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY',
    'http_proxy', 'https_proxy', 'all_proxy',
    'no_proxy', 'NO_PROXY'
]

for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY',
            'http_proxy', 'https_proxy', 'all_proxy',
            'no_proxy', 'NO_PROXY']:
    os.environ.pop(var, None)
    
print("[INFO] ✔ Proxy environment cleared in config module")

# NOW safe to import dotenv and other stuff
from dotenv import load_dotenv

load_dotenv()

# OpenAI / LLM Settings 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

# Pinecone / Vector Store Settings 
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENV")   
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Chunking / Ingestion Settings 
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# General / System Settings 
MAX_RETRIEVAL_CHUNKS = int(os.getenv("MAX_RETRIEVAL_CHUNKS", "2"))

# Validation
if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: OPENAI_API_KEY is missing from .env file!")
if not PINECONE_API_KEY:
    raise ValueError("❌ ERROR: PINECONE_API_KEY is missing from .env file!")
if not PINECONE_INDEX_NAME:
    raise ValueError("❌ ERROR: PINECONE_INDEX_NAME is missing from .env file!")

print("✔ All required environment variables loaded successfully!")