from config import CHUNK_SIZE, CHUNK_OVERLAP, PINECONE_INDEX_NAME, PINECONE_API_KEY
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

def ingest_document(pdf_path: str):
    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {pdf_path}")
    except Exception as e:
        raise RuntimeError(f"Error loading PDF: {e}")

    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        chunks = splitter.split_documents(documents)
        for i, chunk in enumerate(chunks):
            chunk.metadata["source"] = pdf_path
            chunk.metadata["chunk_id"] = i
    except Exception as e:
        raise RuntimeError(f"Error splitting document: {e}")

    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vectorstore = PineconeVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            index_name=PINECONE_INDEX_NAME,
            pinecone_api_key=PINECONE_API_KEY
        )
    except Exception as e:
        raise RuntimeError(f"Error saving to Pinecone: {e}")

    return vectorstore


def auto_ingest_new_document(file_path: str):
    try:
        print(f"Auto-ingesting document: {file_path}")
        ingest_document(file_path)
        print("Ingestion complete")
    except Exception as e:
        print(f"[Error] Auto ingestion failed for {file_path}: {e}")
