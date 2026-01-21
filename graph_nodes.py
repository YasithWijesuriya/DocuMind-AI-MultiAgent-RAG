from agents import route_question
from agents import retrieve_relevant_chunks
from agents import summarize_context
from agents import compare_documents
from agents import synthesize_answer
from agents import validate_answer


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



def synthesis_node(state):
    final = synthesize_answer(state["agent_outputs"])
    state["final_answer"] = final
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