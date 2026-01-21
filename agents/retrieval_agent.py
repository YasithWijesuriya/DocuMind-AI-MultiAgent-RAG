from config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore


def retrieve_relevant_chunks(query: str, top_k: int = 3):
    """
    User question එකට Pinecone වලින් most relevant chunks retrieve කරන function එක
    """
    try:
        embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small"
        )

        vectorstore = PineconeVectorStore(
            index_name=PINECONE_INDEX_NAME,
            pinecone_api_key=PINECONE_API_KEY,
            embedding=embeddings
        )

        relevant_chunks = vectorstore.similarity_search(
            query=query,
            k=top_k
        )

        return relevant_chunks
    except Exception as e:
        print(f"[Error] retrieving relevant chunks: {e}")
        return []