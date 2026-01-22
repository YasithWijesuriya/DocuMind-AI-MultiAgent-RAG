# pipelines/docmind_pipeline.py

from pipelines.graph_nodes import *
from pipelines.graph_state import DocuMindState
from documind_graph import app
from langchain_community.document_loaders import PyPDFLoader
from agents.ingestion_agent import auto_ingest_new_document
from agents import route_question, rewrite_question
from langchain_core.documents import Document
import uuid
import hashlib

def ask(question: str, docs: list[str], auto_ingest: bool = False):
    print(">>> ask() started")
    """
    Main pipeline function.

    :param question: user question
    :param docs: list of document contents OR file paths
    :param auto_ingest: if True, auto-ingest file paths into Pinecone
    """
    loaded_docs = []
    
    try:
        if auto_ingest:
            print(">>> Auto ingest enabled")
            for doc in docs:
                print(f">>> Ingesting: {doc}")
                if doc.endswith(".pdf"):
                    try:
                        auto_ingest_new_document(doc)
                        
                        hasher = hashlib.sha256()
                        with open(doc, "rb") as f:
                            hasher.update(f.read())
                        doc_id = hasher.hexdigest()
                        
                        loader = PyPDFLoader(doc)
                        chunks = loader.load()
                        
                        for chunk in chunks:
                            chunk.metadata["doc_id"] = doc_id
                        
                        loaded_docs.extend(chunks)
                        print(f"[INFO] Document {doc} loaded with doc_id: {doc_id}")
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
            "agent_outputs": [],
            "thread_id": str(uuid.uuid4()),  
            "conversation_history": [],  
            "original_question": "",
            "rewritten_question": "",
            "route": "",
            "final_answer": "",
            "validation": {}
        }

        result = app.invoke(state)
        print(">>> ask() finished")
        print(f">>> Result: {result}")
        return result
    except Exception as e:
        print(f"[Error] Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# 🔹 Add get_route_type function
def get_route_type(question: str) -> str:
    """
    Simple function to determine route type based on the question.
    Returns "summary" if the question seems like a summary request,
    else returns "default".
    """
    summary_keywords = ["summarize", "summary", "overview", "short version"]
    if any(word.lower() in question.lower() for word in summary_keywords):
        return "summary"
    return "default"
