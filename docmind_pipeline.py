from agents import ingest_document
from agents import retrieve_relevant_chunks
from agents import route_question
from agents import summarize_context
from agents import compare_documents
from agents import synthesize_answer
from agents import validate_answer

def ask(question: str, docs: list[str]) -> dict:
    """
    End-to-end DocuMind pipeline
    """

    # Step 1: Router decides which agent
    route = route_question(question)

    agent_outputs = []

    # Step 2: Call the appropriate agent(s)
    if route == "retrieval":
        for doc in docs:
            chunks = retrieve_relevant_chunks(doc)
            combined_chunks = " ".join([c.page_content for c in chunks])
            agent_outputs.append(combined_chunks)

    elif route == "summary":
        for doc in docs:
            summary = summarize_context(doc)
            agent_outputs.append(summary)

    elif route == "compare":
        if len(docs) >= 2:
            result = compare_documents(docs[0], docs[1])
            agent_outputs.append(result)
        else:
            agent_outputs.append("Not enough documents to compare.")

    elif route == "expert":
        # For now, we can use summary as expert placeholder
        for doc in docs:
            expert_summary = summarize_context(doc)
            agent_outputs.append(expert_summary)

    # Step 3: Synthesis
    final_answer = synthesize_answer(agent_outputs)

    # Step 4: Validator
    # Evidence = concatenation of all agent outputs
    evidence_text = "\n\n".join(agent_outputs)
    validation_result = validate_answer(final_answer, evidence_text)

    # Return combined response
    return {
        "route": route,
        "final_answer": final_answer,
        "validation": validation_result
    }
