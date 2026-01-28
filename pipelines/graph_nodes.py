from agents import route_question
from agents import retrieve_relevant_chunks
from agents import summarize_context
from agents import compare_documents
from agents import synthesize_answer
from agents import validate_answer
from agents import expert_analysis
from agents import rewrite_question
import sqlite3
import json 

def truncate_text(text: str, max_chars: int):
    """
    Forcefully cut text to a maximum number of characters
    """
    if not text:
        return ""

    if len(text) > max_chars:
        return text[:max_chars]

    return text

class SQLiteStore:
    def __init__(self, db_path="documind_memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                thread_id TEXT PRIMARY KEY,
                data TEXT
            )
        """)
        self.conn.commit()

    def get(self, thread_id, key):
        cursor = self.conn.execute("SELECT data FROM memory WHERE thread_id=?", (thread_id,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0]).get(key)
        return None

    def put(self, thread_id, key, value):
        cursor = self.conn.execute("SELECT data FROM memory WHERE thread_id=?", (thread_id,))
        row = cursor.fetchone()
        if row:
            data = json.loads(row[0])
            data[key] = value
            self.conn.execute(
                "UPDATE memory SET data=? WHERE thread_id=?",
                (json.dumps(data), thread_id)
            )
        else:
            data = {key: value}
            self.conn.execute(
                "INSERT INTO memory (thread_id, data) VALUES (?, ?)",
                (thread_id, json.dumps(data))
            )
        self.conn.commit()


store = SQLiteStore("documind_memory.db")

def memory_read_node(state):
    thread_id = state.get("thread_id", "default")
    try:
        raw = store.get(thread_id, "conversation")
        if isinstance(raw, dict):
            state["conversation_history"] = raw.get("messages", [])
        else:
            state["conversation_history"] = []
        print("HISTORY LOADED:", state["conversation_history"])
    except Exception as e:
        print(f"[Error] Memory read failed: {e}")
        state["conversation_history"] = []
    return state


def memory_write_node(state):
    print("WRITING MEMORY")
    thread_id = state.get("thread_id", "default")
    try:
        raw = store.get(thread_id, "conversation")
        if isinstance(raw, dict) and isinstance(raw.get("messages"), list):
            history = raw["messages"]
        else:
            history = []

        history.append({
            "role": "user",
            "content": state.get("original_question", "")
        })
        history.append({
            "role": "assistant",
            "content": state.get("final_answer", "")
        })

        store.put(thread_id, "conversation", {"messages": history})
        print("MEMORY SAVED:", history)
    except Exception as e:
        print(f"[Error] Memory write failed: {e}")
    return state


def rewrite_node(state):
    try:
        question = state.get("question", "")
        state["original_question"] = question

        history = state.get("conversation_history") or []

        history_text = "\n".join(
            f"{m.get('role')}: {m.get('content')}"
            for m in history
        )

        print("HISTORY PASSED TO REWRITE:", repr(history_text))
        print("QUESTION:", question)

        rewritten = rewrite_question(
            history_text=history_text,
            question=question
        )

        state["rewritten_question"] = rewritten.strip() if rewritten else question

    except Exception as e:
        print(f"[Error] Rewrite node failed: {e}")
        state["rewritten_question"] = state.get("original_question", "")

    return state


def router_node(state):
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


def retrieval_node(state):
    """
    Main processing node - retrieves chunks from uploaded documents and processes based on route
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
        
        print(f"[INFO] Document namespaces to search: {doc_namespaces}")
        
        all_chunks = []
        
        if doc_namespaces:
            for namespace in doc_namespaces:
                print(f">>> Retrieving chunks from namespace: {namespace}")
                chunks = retrieve_relevant_chunks(query=query, top_k=2, namespace=namespace)
                all_chunks.extend(chunks)
        else:
            print(">>> No document namespaces found, searching all documents")
            chunks = retrieve_relevant_chunks(query=query, top_k=2)
            all_chunks.extend(chunks)

        if route != "summary" and not all_chunks:
            state["agent_outputs"] = ["No relevant context found in the uploaded documents."]
            state["final_answer"] = "I could not find relevant information in the uploaded documents to answer your question."
            return state

        texts = []
        for c in all_chunks:
            source = c.metadata.get('source', 'unknown')
            if '\\' in source:
                source = source.split('\\')[-1]
            elif '/' in source:
                source = source.split('/')[-1]
                
            texts.append(
                f"{c.page_content}\n[source: {source}]"
            )

        retrieved_text = truncate_text("\n\n".join(texts), 6000)
        print(f">>> Retrieved {len(all_chunks)} chunks total")

        # Step 2: Process based on route
        print(f">>> Processing with route: {route}")
        
        if route == "summary":
            print(">>> Summary route detected")
            result = summarize_context(retrieved_text)
            state["agent_outputs"] = [result]
            state["final_answer"] = result

            
        elif route == "expert":
            print(">>> Generating expert analysis...")
            result = expert_analysis(
                context=retrieved_text,
                question=query
            )
            state["agent_outputs"] = [result]
            state["final_answer"] = result
            
        elif route == "retrieval":
            print(">>> Processing retrieval...")
            # For retrieval, still synthesize for clarity
            result = synthesize_answer([retrieved_text])
            state["agent_outputs"] = [result]
            state["final_answer"] = result
            
        else:  # Default
            result = synthesize_answer([retrieved_text])
            state["agent_outputs"] = [result]
            state["final_answer"] = result

    except Exception as e:
        print(f"[Error] Processing node failed: {e}")
        import traceback
        traceback.print_exc()
        state["agent_outputs"] = [f"Error during processing: {str(e)}"]
        state["final_answer"] = f"An error occurred: {str(e)}"
        
    return state


def compare_node(state):
    """
    Special node for comparing documents
    """
    print(">>> ENTERED compare_node")
    docs = state.get("docs", [])

    if len(docs) >= 2:
        try:
            doc_a = truncate_text(docs[0].page_content if hasattr(docs[0], 'page_content') else str(docs[0]), 3000)
            doc_b = truncate_text(docs[1].page_content if hasattr(docs[1], 'page_content') else str(docs[1]), 3000)
            
            result = compare_documents(doc_a, doc_b)
            state["agent_outputs"] = [result]
        except Exception as e:
            print(f"[Error] Compare node failed: {e}")
            state["agent_outputs"] = ["Error comparing documents."]
    else:
        state["agent_outputs"] = ["Not enough documents to compare"]

    return state


def synthesis_node(state):
    """
    Synthesis node - final answer already set by retrieval_node for most routes
    This node only applies synthesis if needed for compare route
    """
    print(">>> ENTERED synthesis_node")
    
    route = state.get("route", "retrieval")
    final_answer = state.get("final_answer")
    
    #  If final_answer already set (from retrieval/summary/expert), skip synthesis
    if final_answer and route != "compare":
        print(f">>> Final answer already set, skipping synthesis")
        return state
    
    outputs = state.get("agent_outputs", [])

    if not outputs:
        state["final_answer"] = "No agent outputs available to synthesize."
        return state

    safe_outputs = []
    
    try:
        safe_outputs = [truncate_text(o, max_chars=4000) for o in outputs if o]

        if not safe_outputs:
            state["final_answer"] = "No valid content to synthesize."
            return state

        final_answer = synthesize_answer(safe_outputs)
        state["final_answer"] = final_answer
        
    except Exception as e:
        print(f"[Error] Synthesis node failed: {e}")
        import traceback
        traceback.print_exc()
        #  Now safe_outputs is always defined
        state["final_answer"] = safe_outputs[0] if safe_outputs else "Error generating answer."
        
    return state


def validator_node(state):
    """
    Validate the final answer against evidence
    """
    print(">>> ENTERED validator_node")
    outputs = state.get("agent_outputs", [])

    if not outputs:
        state["validation"] = {"status": "FAIL", "report": "No evidence provided."}
        return state

    try:
        evidence = "\n\n".join([o for o in outputs if o])
        final_answer = state.get("final_answer", "")
        
        if not final_answer:
            state["validation"] = {"status": "FAIL", "report": "No final answer to validate."}
            return state
        
        result = validate_answer(final_answer, evidence)
        state["validation"] = result
        
    except Exception as e:
        print(f"[Error] Validator node failed: {e}")
        import traceback
        traceback.print_exc()
        state["validation"] = {"status": "ERROR", "report": str(e)}
        
    return state