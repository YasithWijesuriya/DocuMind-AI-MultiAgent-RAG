from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

synthesis_prompt = ChatPromptTemplate.from_template(
    """
You are a synthesis agent in a multi-agent document analysis system.

Your task:
Combine the following agent outputs into a single, clear, and helpful answer.

Rules:
- Do NOT add new information
- Do NOT contradict the agent outputs
- Remove duplication
- Use ONLY the provided content
- Do NOT infer dates, locations, or business types
- If something is not explicitly stated, say "Not mentioned in the document"
- Prefer general explanations over company-specific claims
- Use clear structure and simple language
- If something is uncertain, state it clearly
- Add citations like [source: document_name]
- Do NOT hallucinate sources

Agent outputs:
{agent_outputs}

Return a final, well-structured answer.
"""
)

def synthesize_answer(agent_outputs: list[str]) -> str:

    llm = ChatOpenAI(
        model="gpt-4",
        model_kwargs={"temperature": 0.2} 
    )

    combined_text = "\n\n".join(agent_outputs)

    chain = synthesis_prompt | llm # see : file://./learn.md

    response = chain.invoke(
        {"agent_outputs": combined_text}
    )

    return str(response.content)
