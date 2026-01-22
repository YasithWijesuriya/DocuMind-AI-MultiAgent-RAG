import hashlib
import time
from config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    PINECONE_INDEX_NAME,
    PINECONE_API_KEY
)

from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone


def file_hash(path: str) -> str:
    """Generate unique hash per file"""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def is_document_ingested(doc_id: str) -> bool:
    """Check if document already in Pinecone"""
    try:
        if not PINECONE_INDEX_NAME:
            raise ValueError("PINECONE_INDEX_NAME is missing.")

        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        stats = index.describe_index_stats()
        
        return doc_id in stats.get("namespaces", {})
    except Exception as e:
        print(f"[Error] Checking document: {e}")
        return False


def ingest_document(pdf_path: str, force: bool = False):
    """
    Ingest PDF into Pinecone vector store
    
    :param pdf_path: Path to PDF file
    :param force: Force re-ingestion even if already exists
    """
    doc_id = file_hash(pdf_path)

    if not PINECONE_INDEX_NAME:
        raise ValueError("PINECONE_INDEX_NAME is missing. Check your .env file.")

    if is_document_ingested(doc_id) and not force:
        print(f"[SKIPPED] Document already ingested: {pdf_path}")
        return {"status": "skipped", "doc_id": doc_id}

    print(f"[INGESTING] {pdf_path}")

    try:
        loader = UnstructuredPDFLoader(pdf_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

        chunks = splitter.split_documents(documents)

        for i, chunk in enumerate(chunks):
            chunk.metadata["source"] = pdf_path
            chunk.metadata["chunk_id"] = i
            chunk.metadata["doc_id"] = doc_id

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)

        PineconeVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            index_name=PINECONE_INDEX_NAME,
            pinecone_api_key=PINECONE_API_KEY,
            namespace=doc_id
        )

        print(f"[INGESTED] {pdf_path} with {len(chunks)} chunks")
        return {"status": "ingested", "doc_id": doc_id, "chunks": len(chunks)}

    except Exception as e:
        print(f"[Error] Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def auto_ingest_new_document(file_path: str):
    """
    Wrapper for pipeline - only ingest if needed
    
    :param file_path: Path to PDF file
    """
    try:
        time.sleep(0.5)  # Reduced sleep
        return ingest_document(file_path)
    except Exception as e:
        print(f"[Error] Auto ingestion failed: {e}")
        return {"status": "error", "error": str(e)}