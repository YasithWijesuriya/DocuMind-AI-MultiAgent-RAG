from pipelines.graph_nodes import *
from pipelines.graph_state import DocuMindState
from documind_graph import app
from langchain_community.document_loaders import PyPDFLoader
from agents.ingestion_agent import auto_ingest_new_document
from langchain_core.documents import Document

def ask(question: str, docs: list[str], auto_ingest: bool = False):
    """
    Main pipeline function.

    :param question: user question
    :param docs: list of document contents OR file paths
    :param auto_ingest: if True, auto-ingest file paths into Pinecone
    """
    loaded_docs = []
    
    try:
        if auto_ingest:
            for doc in docs:
                if doc.endswith(".pdf"):
                    try:
                        auto_ingest_new_document(doc)
                        loader = PyPDFLoader(doc)
                        chunks = loader.load()  # returns list of Document objects with metadata
                        loaded_docs.extend(chunks)
                    except Exception as e:
                        print(f"[Error] Auto-ingestion failed for {doc}: {e}")
                
                else:
                    # wrap plain text in Document object
                    loaded_docs.append(Document(page_content=doc, metadata={"source": "user_input"}))
        else:
            for doc in docs:
                if isinstance(doc, str):
                    loaded_docs.append(Document(page_content=doc, metadata={"source": "user_input"}))
                else:
                    loaded_docs.append(doc)

        state: DocuMindState = {
            "question": question,
            "docs": loaded_docs,
            "agent_outputs": []
        }

        result = app.invoke(state)
        return result
    except Exception as e:
        print(f"[Error] Pipeline execution failed: {e}")
        return {"error": str(e)}