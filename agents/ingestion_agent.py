import hashlib
import os
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from config import CHUNK_SIZE, CHUNK_OVERLAP, PINECONE_INDEX_NAME, PINECONE_API_KEY


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
        index = pc.Index(str(PINECONE_INDEX_NAME))
        stats = index.describe_index_stats()
        
        namespaces = stats.namespaces if hasattr(stats, 'namespaces') else {}
        return doc_id in namespaces
        
    except Exception as e:
        print(f"[Error] Checking document: {e}")
        return False


def ingest_document(pdf_path: str, force: bool = False) -> dict:
    """
    Ingest PDF into Pinecone vector store using new Pinecone SDK
    
    Args:
        pdf_path: Path to PDF file
        force: Force re-ingestion even if already exists
        
    Returns:
        Dictionary with status, doc_id, and chunks count
    """
    doc_id = file_hash(pdf_path)

    if not PINECONE_INDEX_NAME:
        raise ValueError("PINECONE_INDEX_NAME is missing. Check your .env file.")

    if is_document_ingested(doc_id) and not force:
        print(f"[SKIPPED] Document already ingested: {pdf_path}")
        return {"status": "skipped", "doc_id": doc_id}

    print(f"[INGESTING] {pdf_path}")

    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        print(f"[INFO] Loaded {len(documents)} pages from PDF")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        chunks = splitter.split_documents(documents)
        print(f"[INFO] Split into {len(chunks)} chunks")

        clean_source = os.path.basename(pdf_path)

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=None  
        )
        print(f"[INFO] Creating embeddings for {len(chunks)} chunks...")

        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(str(PINECONE_INDEX_NAME))

        vectors = []
        for i, chunk in enumerate(chunks):
            try:
                embedding = embeddings.embed_query(chunk.page_content)
                
                vectors.append({
                    "id": f"{doc_id}_{i}",
                    "values": embedding,
                    "metadata": {
                        "text": chunk.page_content[:1000],  
                        "source": clean_source,             
                        "chunk_id": i,
                        "doc_id": doc_id
                    }
                })
                
                if (i + 1) % 10 == 0:
                    print(f"[INFO] Embedded {i + 1}/{len(chunks)} chunks")
                    
            except Exception as e:
                print(f"[Warning] Failed to embed chunk {i}: {e}")
                continue

        batch_size = 100
        total_upserted = 0
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            try:
                index.upsert(vectors=batch, namespace=doc_id)
                total_upserted += len(batch)
                print(f"[INFO] Upserted batch {i//batch_size + 1}: {len(batch)} vectors")
            except Exception as e:
                print(f"[Error] Failed to upsert batch {i//batch_size + 1}: {e}")
                continue

        print(f"[SUCCESS] ✔ Ingested {pdf_path}")
        print(f"[SUCCESS] Total chunks: {len(chunks)}, Successfully upserted: {total_upserted}")
        
        return {
            "status": "ingested", 
            "doc_id": doc_id, 
            "chunks": len(chunks),
            "upserted": total_upserted
        }

    except Exception as e:
        print(f"[Error] ❌ Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def auto_ingest_new_document(file_path: str) -> dict:
    """
    Wrapper for pipeline - only ingest if needed
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Dictionary with ingestion status
    """
    try:
        print(f"[INFO] Auto-ingesting: {file_path}")
        time.sleep(0.5)
        result = ingest_document(file_path)
        print(f"[INFO] Auto-ingest result: {result.get('status')}")
        return result
    except Exception as e:
        print(f"[Error] Auto ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}