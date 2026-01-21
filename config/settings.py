import os 
from dotenv import load_dotenv
load_dotenv()

#  OpenAI / LLM Settings 
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0))

#  Pinecone / Vector Store Settings 
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENV")   
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

#  Chunking / Ingestion Settings 
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

#  General / System Settings 
MAX_RETRIEVAL_CHUNKS = int(os.getenv("MAX_RETRIEVAL_CHUNKS", 5))