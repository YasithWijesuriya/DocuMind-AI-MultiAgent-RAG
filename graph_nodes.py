from agents import route_question
from agents import retrieve_relevant_chunks
from agents import summarize_context
from agents import compare_documents
from agents import synthesize_answer
from agents import validate_answer
from agents import expert_analysis
from agents import rewrite_question
from langgraph.store.memory import InMemoryStore


store = InMemoryStore()

def memory_read_node(state):
    thread_id = state.get("thread_id", "default")
    raw = store.get(thread_id, "conversation")

    if isinstance(raw, dict):
        state["conversation_history"] = raw.get("messages", [])
    else:
        state["conversation_history"] = []
    return state


def memory_write_node(state):
    thread_id = state.get("thread_id", "default")

    raw = store.get(thread_id, "conversation")

    if isinstance(raw, dict) and isinstance(raw.get("messages"), list):
        history = raw["messages"]
    else:
        history = []

    history.append({
        "role": "user",
        "content": state["original_question"]
    })

    history.append({
        "role": "assistant",
        "content": state["final_answer"]
    })

    store.put(
        thread_id,
        "conversation",
        {"messages": history}
    )
    return state
 
def rewrite_node(state):
    state["original_question"] = state["question"]
    history_text = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in state.get("conversation_history", [])
    )
    rewritten = rewrite_question(
        history_text=history_text,
        question=state["question"]
    )
    state["question"] = rewritten
    return state



def router_node(state):
    route = route_question(state["question"])
    state["route"] = route
    return state

            # state["question"] → question string එක
            # ඒක route_question() ට pass කරනවා
            # route_question() → "summary" return කරනවා
            # ඒ value එක route variable එකට assign වෙනවා
            # state dictionary එක ඇතුළට දානවා:



def retrieval_node(state):
    chunks = retrieve_relevant_chunks(
        query=state["question"],  # user question
        top_k=5
    )

    combined_chunks = " ".join([c.page_content for c in chunks]) #file://./agents/learn.md
    state["agent_outputs"] = [combined_chunks]
    return state
        # retrieve relevant chunks based on the question
        # update the state with agent outputs
        


def summary_node(state):
    outputs = [summarize_context(doc) for doc in state["docs"]] #where is doc came from?: file://./agents/learn.md
    state["agent_outputs"] = outputs
    return state
        # for each document, summarize the context
        # update the state with agent outputs



def compare_node(state):
    if len(state["docs"]) >= 2:
        result = compare_documents(state["docs"][0], state["docs"][1])
        state["agent_outputs"] = [result]  #?[result] what is the meaning of this brackets? this is used for creating a list with single element and no get string error
    else:
        state["agent_outputs"] = ["Not enough documents"]
    return state
        # if at least 2 documents, compare the first two
        # update the state with agent outputs

def expert_node(state):
    combined_docs = " ".join(state["docs"])

    result = expert_analysis(
        context=combined_docs,
        question=state["question"]
    )
    state["agent_outputs"] = [result]
    return state



def synthesis_node(state):
    output_with_sources = []
    for output in state["agent_outputs"]:
        output_with_sources.append(f"{output}\n\n[source: document_name]")  # Placeholder for actual source

    final_answer = synthesize_answer(output_with_sources)
    state["final_answer"] = final_answer
    return state
        # synthesize the final answer from agent outputs
        # update the state with the final answer


def validator_node(state):
    evidence = "\n\n".join(state["agent_outputs"])
    result = validate_answer(state["final_answer"], evidence)
    state["validation"] = result
    return state
        # concatenate all agent outputs as evidence
        # validate the final answer against the evidence
        # update the state with the validation result