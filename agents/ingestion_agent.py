from config import (CHUNK_SIZE,CHUNK_OVERLAP,PINECONE_INDEX_NAME,PINECONE_API_KEY)
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore


def ingest_document(pdf_path: str):
    """
    PDF document එක read කරලා Pinecone vector store එකට save කරන function එක
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = splitter.split_documents(documents)

    for i,chunk in enumerate(chunks): # see : file://./learn.md
        chunk.metadata["source"] = pdf_path
        chunk.metadata["chunk_id"] = i

    embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
    )

    vectorstore = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=PINECONE_INDEX_NAME,
        pinecone_api_key=PINECONE_API_KEY
    )

    return vectorstore