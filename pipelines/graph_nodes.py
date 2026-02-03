import sys
import os
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents import route_question
from agents import retrieve_relevant_chunks
from agents import summarize_context,format_summary_result
from agents import compare_documents, format_comparison_result
from agents import synthesize_answer, format_synthesis_output
from agents import validate_answer, format_validation_result
from agents import expert_analysis, format_expert_result
from agents import rewrite_question
import json
from typing import Optional, Any
import hashlib


class VercelFriendlyStore:
    """
    Storage backend compatible with Vercel's serverless environment
    Uses /tmp for persistence (ephemeral) with optional fallback
    """
    
    def __init__(self, db_path: str = "documind_memory.db"):
        """
        Initialize store with runtime path
        
        Args:
            db_path: Path to store database (in /tmp for Vercel)
        """
        self.runtime_db_path = os.path.join("/tmp", os.path.basename(db_path))
        self.memory_cache: dict = {}  #! Fallback in-memory cache
        self._ensure_storage()

    def _ensure_storage(self):
        """Ensure storage directory exists"""
        os.makedirs("/tmp", exist_ok=True)

    def get(self, thread_id: str, key: str) -> Optional[dict]:
        """
        Retrieve data from storage
        
        Args:
            thread_id: Thread identifier
            key: Data key
            
        Returns:
            Retrieved data or None
        """
        try:
            #! Try file-based storage first
            if os.path.exists(self.runtime_db_path):
                with open(self.runtime_db_path, 'r') as f:
                    content = f.read().strip()
                   
                    if content:
                        data = json.loads(content)
                        return data.get(thread_id, {}).get(key)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARNING] File storage read failed: {e}")
        
        #! Fallback to memory cache
        return self.memory_cache.get(thread_id, {}).get(key)


    def put(self, thread_id: str, key: str, value: Any) -> bool:
        """
        Store data in storage
        
        Args:
            thread_id: Thread identifier
            key: Data key
            value: Data to store
            
        Returns:
            True if successful
        """
        try:
            #! Try file-based storage
            data = {}
            if os.path.exists(self.runtime_db_path):
                try:
                    with open(self.runtime_db_path, 'r') as f:
                        content = f.read().strip()
                        if content:  
                            data = json.loads(content)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"[WARNING] File storage read before write failed: {e}, starting fresh")
                    data = {}
            
            if thread_id not in data:
                data[thread_id] = {}
            
            data[thread_id][key] = value
            
            with open(self.runtime_db_path, 'w') as f:
                json.dump(data, f)
                
        except Exception as e:
            print(f"[WARNING] File storage write failed: {e}, using memory")
        
        #! Always maintain memory cache as fallback
        if thread_id not in self.memory_cache:
            self.memory_cache[thread_id] = {}
        self.memory_cache[thread_id][key] = value
        
        return True
    
store = VercelFriendlyStore("documind_memory.db")


def truncate_text(text: str, max_chars: int = 6000) -> str:
    """
    Truncate text to maximum characters (for API limits)
    
    Args:
        text: Text to truncate
        max_chars: Maximum character limit
        
    Returns:
        Truncated text
    """
    if not text:
        return ""
    return text[:max_chars] if len(text) > max_chars else text


def memory_read_node(state: dict) -> dict:
    """
    Read conversation history from storage
    
    Args:
        state: Current state
        
    Returns:
        Updated state with conversation history
    """
    thread_id = state.get("thread_id", "default")
    try:
        raw = store.get(thread_id, "conversation")
        if isinstance(raw, dict) and "messages" in raw:
            state["conversation_history"] = raw.get("messages", [])
        else:
            state["conversation_history"] = []
        print(f"[INFO] Memory loaded for thread: {thread_id}")
    except Exception as e:
        print(f"[Error] Memory read failed: {e}")
        state["conversation_history"] = []
    return state


def memory_write_node(state: dict) -> dict:
    """
    Write conversation to storage
    
    Args:
        state: Current state with final answer
        
    Returns:
        Updated state
    """
    thread_id = state.get("thread_id", "default")
    try:
        raw = store.get(thread_id, "conversation")
        if isinstance(raw, dict) and isinstance(raw.get("messages"), list):
            history = raw["messages"]
        else:
            history = []

        # Add new exchange
        history.append({
            "role": "user",
            "content": state.get("original_question", "")
        })
        history.append({
            "role": "assistant",
            "content": state.get("final_answer", "")
        })

        store.put(thread_id, "conversation", {"messages": history})
        print(f"[INFO] Memory saved for thread: {thread_id}")
    except Exception as e:
        print(f"[Error] Memory write failed: {e}")
    return state


def rewrite_node(state: dict) -> dict:
    """
    Rewrite question for clarity using conversation history
    
    Args:
        state: Current state
        
    Returns:
        State with rewritten question
    """
    try:
        question = state.get("question", "")
        state["original_question"] = question

        history = state.get("conversation_history") or []
        history_text = "\n".join(
            f"{m.get('role', 'unknown')}: {m.get('content', '')}"
            for m in history
        )

        rewritten = rewrite_question(history_text=history_text, question=question)
        state["rewritten_question"] = rewritten.strip() if rewritten else question

    except Exception as e:
        print(f"[Error] Rewrite node failed: {e}")
        state["rewritten_question"] = state.get("original_question", "")

    return state


def router_node(state: dict) -> dict:
    """
    Route question to appropriate agent
    
    Args:
        state: Current state
        
    Returns:
        State with route decision
    """
    try:
        q = state.get("rewritten_question", "")
        if not q:
            print("[Warning] Empty rewritten question, defaulting to retrieval")
            state["route"] = "retrieval"
            return state
            
        route = route_question(q)
        state["route"] = route
    except Exception as e:
        print(f"[Error] Router node failed: {e}")
        state["route"] = "retrieval"
    return state


def retrieval_node(state: dict) -> dict:
    """
    Retrieve relevant chunks and process based on route
    
    Args:
        state: Current state with question and documents
        
    Returns:
        State with agent outputs and final answer
    """
    print(">>> ENTERED retrieval_node")

    query = state.get("rewritten_question", "")
    route = state.get("route", "retrieval")
    docs = state.get("docs", [])
    
    if not query:
        print("[Warning] Empty query in retrieval node")
        state["agent_outputs"] = ["No query provided."]
        state["final_answer"] = "No query provided."
        return state

    try:
        doc_namespaces = set()
        for doc in docs:
            if hasattr(doc, 'metadata') and 'doc_id' in doc.metadata:
                doc_namespaces.add(doc.metadata['doc_id'])
        
        print(f"[INFO] Document namespaces: {len(doc_namespaces)}")
        
        all_chunks = []
        
        if doc_namespaces:
            for namespace in doc_namespaces:
                chunks = retrieve_relevant_chunks(query=query, top_k=2, namespace=namespace)
                all_chunks.extend(chunks)
        else:
            chunks = retrieve_relevant_chunks(query=query, top_k=2)
            all_chunks.extend(chunks)

        if route != "summary" and not all_chunks:
            state["agent_outputs"] = ["No relevant context found."]
            state["final_answer"] = "I could not find relevant information to answer your question."
            return state

        #! Format chunks with sources
        texts = []
        for c in all_chunks:
            source = c.metadata.get('source', 'unknown')
            #! Clean up source path
            if '\\' in source:
                source = source.split('\\')[-1]
            elif '/' in source:
                source = source.split('/')[-1]
                
            texts.append(f"{c.page_content}\n[source: {source}]")

        retrieved_text = truncate_text("\n\n".join(texts))
        print(f">>> Retrieved {len(all_chunks)} chunks")

        #! Process based on route
        if route == "summary":
            result = summarize_context(retrieved_text)
            formatted = format_summary_result(result)
            state["agent_outputs"] = [formatted]
            state["final_answer"] = formatted
            
        elif route == "expert":
            result = expert_analysis(context=retrieved_text, question=query)
            formatted = format_expert_result(result)
            state["agent_outputs"] = [formatted]
            state["final_answer"] = formatted
            
        elif route == "compare":
            result = compare_documents(retrieved_text, "")
            formatted = format_comparison_result(result)
            state["agent_outputs"] = [formatted]
            state["final_answer"] = formatted
            
        elif route == "retrieval":
            result = synthesize_answer([retrieved_text])
            formatted = format_synthesis_output(result)
            state["agent_outputs"] = [formatted]
            state["final_answer"] = formatted
            
        else:  # Default
            result = synthesize_answer([retrieved_text])
            formatted = format_synthesis_output(result)
            state["agent_outputs"] = [formatted]
            state["final_answer"] = formatted

    except Exception as e:
        print(f"[Error] Retrieval node failed: {e}")
        import traceback
        traceback.print_exc()
        state["agent_outputs"] = [f"Error: {str(e)}"]
        state["final_answer"] = f"An error occurred: {str(e)}"
        
    return state


def compare_node(state: dict) -> dict:
    """
    Compare multiple documents
    
    Args:
        state: Current state
        
    Returns:
        State with comparison result
    """
    print(">>> ENTERED compare_node")
    docs = state.get("docs", [])

    if len(docs) >= 2:
        try:
            doc_a = truncate_text(
                docs[0].page_content if hasattr(docs[0], 'page_content') else str(docs[0]), 
                3000
            )
            doc_b = truncate_text(
                docs[1].page_content if hasattr(docs[1], 'page_content') else str(docs[1]), 
                3000
            )
            
            result = compare_documents(doc_a, doc_b)
            formatted = format_comparison_result(result)
            state["agent_outputs"] = [formatted]
        except Exception as e:
            print(f"[Error] Compare node failed: {e}")
            state["agent_outputs"] = ["Error comparing documents."]
    else:
        state["agent_outputs"] = ["Not enough documents to compare."]

    return state


def synthesis_node(state: dict) -> dict:
    """
    Synthesis node - synthesizes final answer if needed
    
    Args:
        state: Current state
        
    Returns:
        State with final synthesized answer
    """
    print(">>> ENTERED synthesis_node")
    
    route = state.get("route", "retrieval")
    final_answer = state.get("final_answer")
    
    #! Skip synthesis if answer already set
    if final_answer and route != "compare":
        return state
    
    outputs = state.get("agent_outputs", [])
    if not outputs:
        state["final_answer"] = "No outputs to synthesize."
        return state

    try:
        safe_outputs = [truncate_text(o, 4000) for o in outputs if o]
        if not safe_outputs:
            state["final_answer"] = "No valid content."
            return state

        result = synthesize_answer(safe_outputs)
        formatted = format_synthesis_output(result)
        state["final_answer"] = formatted
        
    except Exception as e:
        print(f"[Error] Synthesis failed: {e}")
        state["final_answer"] = outputs[0] if outputs else "Error generating answer."
        
    return state


def validator_node(state: dict) -> dict:
    """
    Validate final answer against evidence
    
    Args:
        state: Current state
        
    Returns:
        State with validation result
    """
    print(">>> ENTERED validator_node")
    outputs = state.get("agent_outputs", [])

    if not outputs:
        state["validation"] = {"status": "FAIL", "report": "No evidence."}
        return state

    try:
        evidence = "\n\n".join([o for o in outputs if o])
        final_answer = state.get("final_answer", "")
        
        if not final_answer:
            state["validation"] = {"status": "FAIL", "report": "No answer."}
            return state
        
        result = validate_answer(final_answer, evidence)
        formatted = format_validation_result(result)
        state["validation"] = {"status": result.status, "report": formatted}
        
    except Exception as e:
        print(f"[Error] Validation failed: {e}")
        state["validation"] = {"status": "ERROR", "report": str(e)}
        
    return state