from config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from typing import Optional, List

def retrieve_relevant_chunks(query: str, top_k: int = 2, namespace: Optional[str] = None):
    """
    Retrieve most relevant chunks from Pinecone for a given query
    
    :param query: User's question/query
    :param top_k: Number of chunks to retrieve
    :param namespace: Optional - specific document namespace to search within
    """
    try:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

        vectorstore = PineconeVectorStore(
            index_name=PINECONE_INDEX_NAME,
            pinecone_api_key=PINECONE_API_KEY,
            embedding=embeddings,
            namespace=namespace
        )

        results = vectorstore.similarity_search(
            query=query,
            k=top_k
        )

        print(f"[INFO] Retrieved {len(results)} chunks from {namespace or 'all'}")
        return results

    except Exception as e:
        print(f"[Error] Retrieving chunks: {e}")
        return []


def get_available_namespaces():
    """
    Get all available document namespaces from Pinecone
    """
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME or "")
        
        stats = index.describe_index_stats()
        namespaces = list(stats.get("namespaces", {}).keys())
        
        print(f"[INFO] Available namespaces: {namespaces}")
        return namespaces
        
    except Exception as e:
        print(f"[Error] Getting namespaces: {e}")
        return []