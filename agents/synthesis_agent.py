from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import re

synthesis_prompt = ChatPromptTemplate.from_template(
    """
You are a synthesis agent in a multi-agent document analysis system.

Your task:
Combine the following agent outputs into ONE clear, well-structured, and professional answer.

STRICT RULES:
- Use ONLY the information provided in the agent outputs
- Do NOT add new information
- Do NOT contradict any agent output
- Remove all duplication
- Do NOT infer dates, locations, statistics, or business types
- If information is missing or unclear, explicitly say:
  "Not mentioned in the document"
- If information is uncertain, state that it is uncertain
- Do NOT hallucinate facts or sources
- PRESERVE all citations exactly as given (e.g. [source: ...])
- Do NOT create new citations
- Use clear academic language
- Prefer general explanations over organization-specific claims

STRUCTURE & FORMAT (MANDATORY):
- Write in Markdown format
- Use ONE main title with `#`
- Use clear section headings with `##`
- Leave a clear blank line between:
  - headings and content
  - paragraphs
- Separate facts clearly
- Use bullet points where appropriate
- Write complete, well-formed sentences
- Maintain a professional academic tone

CITATIONS:
- Place citations on a NEW LINE after the relevant section
- Keep citation format exactly as provided
- Example:
  [source: document_name]

AGENT OUTPUTS:
{agent_outputs}

Return a FINAL, clean, and well-structured answer that strictly follows all rules above.

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