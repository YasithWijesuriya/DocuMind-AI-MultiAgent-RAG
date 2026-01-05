import os
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
load_dotenv()

def retrieve_relevant_chunks(query: str, top_k: int = 5):
    """
    User question එකට Pinecone වලින් most relevant chunks retrieve කරන function එක
    """
    embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
    )

    vectorstore = PineconeVectorStore(
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
        embedding=embeddings
    )

    relevant_chunks = vectorstore.similarity_search(
        query=query,
        k=top_k
    )

    return relevant_chunks