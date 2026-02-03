from config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from typing import List, Optional
from langchain_core.documents import Document


def retrieve_relevant_chunks(
    query: str, 
    top_k: int = 2, 
    namespace: Optional[str] = None
) -> List[Document]:
    """Retrieve most relevant chunks from Pinecone for a given query"""
    
    if not PINECONE_INDEX_NAME:
        print("[Error] PINECONE_INDEX_NAME not configured")
        return []
    
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small",api_key=None)
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(str(PINECONE_INDEX_NAME))
        
        query_embedding = embeddings.embed_query(query)
        response = index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True
        )

        documents: List[Document] = []
        
        matches = response.get('matches', []) if hasattr(response, 'get') else response.matches  # type: ignore
        
        for match in matches:
            meta = match.get('metadata', {}) if hasattr(match, 'get') else match.metadata  # type: ignore
            
            documents.append(Document(
                page_content=str(meta.get('text', '') if hasattr(meta, 'get') else getattr(meta, 'text', '')),
                metadata={
                    "source": str(meta.get('source', '') if hasattr(meta, 'get') else getattr(meta, 'source', '')),
                    "chunk_id": int(meta.get('chunk_id', 0) if hasattr(meta, 'get') else getattr(meta, 'chunk_id', 0)),
                    "doc_id": str(meta.get('doc_id', '') if hasattr(meta, 'get') else getattr(meta, 'doc_id', '')),
                    "score": float(match.get('score', 0.0) if hasattr(match, 'get') else match.score)  # type: ignore
                }
            ))

        print(f"[INFO] Retrieved {len(documents)} chunks")
        return documents

    except Exception as e:
        print(f"[Error] Retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_available_namespaces() -> List[str]:
    """Get all available document namespaces from Pinecone"""
    
    if not PINECONE_INDEX_NAME:
        print("[Error] PINECONE_INDEX_NAME not configured")
        return []
    
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(str(PINECONE_INDEX_NAME))
        stats = index.describe_index_stats()
        
        ns_dict = stats.get('namespaces', {}) if hasattr(stats, 'get') else stats.namespaces  
        namespaces = list(ns_dict.keys()) if ns_dict else []
        
        print(f"[INFO] Namespaces: {namespaces}")
        return namespaces
        
    except Exception as e:
        print(f"[Error] Failed to get namespaces: {e}")
        return []