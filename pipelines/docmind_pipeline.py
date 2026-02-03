import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from graph_nodes import *
from graph_state import DocuMindState
from documind_graph import documind_graph
from agents import ingest_document  
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
import uuid
import hashlib


def ask(question: str, docs: list[str], auto_ingest: bool = False) -> dict:
    """
    Main pipeline function - orchestrates multi-agent document analysis
    
    Args:
        question: User's question
        docs: List of document contents or file paths
        auto_ingest: Whether to auto-ingest PDFs into vector store
        
    Returns:
        Dictionary with final_answer and validation results
    """
    print(">>> ask() pipeline started")
    loaded_docs = []
    
    try:
        for doc in docs:
            if isinstance(doc, str) and doc.endswith(".pdf") and os.path.exists(doc):
                try:
                    #! Generate doc_id from file hash
                    hasher = hashlib.sha256()
                    with open(doc, "rb") as f:
                        hasher.update(f.read())
                    doc_id = hasher.hexdigest()

                    #! Ingest PDF into Pinecone
                    if auto_ingest:
                        print(f"[INFO] Running ingestion for: {doc}")
                        ingest_result = ingest_document(doc, force=False)
                        print(f"[INFO] Ingestion status: {ingest_result.get('status')}")
                        print(f"[INFO] Ingestion details: {ingest_result}")

                    #!  Load PDF pages as LangChain Documents
                    loader = PyPDFLoader(doc)
                    chunks = loader.load()

                    #!  Attach doc_id and source to each chunk metadata
                    for chunk in chunks:
                        chunk.metadata["doc_id"] = doc_id
                        if "source" not in chunk.metadata:
                            chunk.metadata["source"] = os.path.basename(doc)

                    loaded_docs.extend(chunks)
                    print(f"[INFO] PDF loaded: {doc} ({len(chunks)} pages)")

                except Exception as e:
                    print(f"[Error] Failed to process {doc}: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                #! Plain text input
                loaded_docs.append(
                    Document(page_content=str(doc), metadata={"source": "user_input"})
                )

        print(f"[INFO] Total documents loaded: {len(loaded_docs)}")

        #! If no docs loaded, return error
        if not loaded_docs:
            return {
                "final_answer": "No documents were loaded. Please upload a valid PDF file.",
                "validation": {"status": "ERROR"},
                "route": "",
                "thread_id": ""
            }

        
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

        #! Execute graph
        result = documind_graph.invoke(state)
        print(">>> Pipeline completed successfully")
        
        return {
            "final_answer": result.get("final_answer", ""),
            "validation": result.get("validation", {}),
            "route": result.get("route", ""),
            "thread_id": result.get("thread_id", "")
        }
        
    except Exception as e:
        print(f"[Error] Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "final_answer": f"Pipeline error: {str(e)}",
            "validation": {"status": "ERROR"},
            "error": str(e)
        }


def get_route_type(question: str) -> str:
    """
    Determine route type from question keywords
    
    Args:
        question: User's question
        
    Returns:
        Route type: "summary" or "default"
    """
    summary_keywords = ["summarize", "summary", "overview", "short version", "brief"]
    
    if any(keyword.lower() in question.lower() for keyword in summary_keywords):
        return "summary"
    
    return "default"