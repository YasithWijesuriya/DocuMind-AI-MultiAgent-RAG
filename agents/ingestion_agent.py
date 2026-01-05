from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from dotenv import load_dotenv
load_dotenv()
import os

def ingest_document(pdf_path: str):
    """
    PDF document එක read කරලා Pinecone vector store එකට save කරන function එක
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
    )

    vectorstore = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        pinecone_api_key=os.getenv("PINECONE_API_KEY")
    )

    return vectorstore