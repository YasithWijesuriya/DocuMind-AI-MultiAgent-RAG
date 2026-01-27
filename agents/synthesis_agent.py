from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import re

synthesis_prompt = ChatPromptTemplate.from_template(
"""
You are a synthesis agent in a multi-agent document analysis system.

Your task:
Combine the provided agent outputs into ONE clear, concise, and professional answer in a fully structured format.

STRICT RULES:
- Use ONLY the information provided in the agent outputs.
- Do NOT add new information, make assumptions, or contradict any agent output.
- Remove all duplication.
- If information is missing or unclear, explicitly state: "Not mentioned in the document."
- If information is uncertain, explicitly state it is uncertain.
- Do NOT hallucinate facts, dates, locations, statistics, or business types.
- PRESERVE all citations exactly as provided (e.g., [source: ...]).
- Do NOT create new citations.
- Use professional and academic language.
- Keep your answer concise; provide only what is needed to answer the question directly.
- Aim to keep answers under 200 words for simple questions.
- Provide one direct answer first, then structured sections.

OUTPUT FORMAT:
- Markdown format only.
- Use ONE main title in **bold** with `#`.
- Sections must include **bold headings** with `##`:
  1. **Direct Answer** – one or two sentence direct response.
  2. **Key Information** – list all explicit facts from the agent outputs.
  3. **Uncertainties** – list any information that is explicitly stated as uncertain.
  4. **Missing Information** – list anything explicitly missing or not mentioned in the sources.
  5. **Details from sources** – include optional additional context, ONLY if directly mentioned in the agent outputs.
- Use bullet points for lists.
- Leave a blank line between headings and content.
- Place citations immediately below the relevant section, preserving the format exactly.

EXAMPLE STRUCTURE:


- Short, one-sentence explanation.

- Fact 1.
- Fact 2.

- Description of uncertain fact.

- Description of missing fact.

- Additional context explicitly mentioned in the sources.

[Insert citation exactly as given]

AGENT OUTPUTS:
{agent_outputs}

Return a FINAL answer strictly following this format.
"""
)



def extract_sources(text: str) -> list:
    """
    Extract [source: ...] citations from text
    """
    pattern = r'\[source:\s*([^\]]+)\]'
    sources = re.findall(pattern, text)
    return list(set(sources))  


def synthesize_answer(agent_outputs: list[str]) -> str:
    """
    Synthesize final answer from agent outputs while preserving sources
    """
    try:
        all_sources = []
        for output in agent_outputs:
            sources = extract_sources(output)
            all_sources.extend(sources)
        
        
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
            if "[source:" not in final_answer:
                sources_text = "\n\n**Sources:**\n" + "\n".join([f"- {source}" for source in all_sources])
                final_answer += sources_text
        
        return final_answer
        
    except Exception as e:
        print(f"[Error] Synthesis failed: {e}")
        import traceback
        traceback.print_exc()
        return "Error generating final answer."