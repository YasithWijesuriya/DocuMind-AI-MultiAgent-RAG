from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import re

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
- PRESERVE all [source: ...] citations from the original content
- Do NOT hallucinate sources
- Add citations at the end: [source: document_name]

Agent outputs:
{agent_outputs}

Return a final, well-structured answer with proper citations.
"""
)

def extract_sources(text: str) -> list:
    """
    Extract [source: ...] citations from text
    """
    pattern = r'\[source:\s*([^\]]+)\]'
    sources = re.findall(pattern, text)
    return list(set(sources))  # Remove duplicates


def synthesize_answer(agent_outputs: list[str]) -> str:
    """
    Synthesize final answer from agent outputs while preserving sources
    """
    try:
        all_sources = []
        for output in agent_outputs:
            sources = extract_sources(output)
            all_sources.extend(sources)
        
        # Remove duplicates
        all_sources = list(set(all_sources))
        
        print(f"[INFO] Found sources: {all_sources}")

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2
        )

        combined_text = "\n\n".join(agent_outputs)

        chain = synthesis_prompt | llm

        response = chain.invoke(
            {"agent_outputs": combined_text}
        )

        final_answer = str(response.content)
        
        if all_sources:
            # Check if answer already has sources
            if "[source:" not in final_answer:
                sources_text = "\n\n**Sources:**\n" + "\n".join([f"- {source}" for source in all_sources])
                final_answer += sources_text
        
        return final_answer
        
    except Exception as e:
        print(f"[Error] Synthesis failed: {e}")
        import traceback
        traceback.print_exc()
        return "Error generating final answer."