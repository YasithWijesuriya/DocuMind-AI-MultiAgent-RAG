from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import re

summary_prompt = ChatPromptTemplate.from_template(
"""
You are a professional document summarization agent.

GOAL:
Produce a clear, accurate, and well-structured summary of the document content provided.

STRICT RULES (MANDATORY):
- Use ONLY information explicitly stated in the document.
- Do NOT add assumptions, interpretations, or external knowledge.
- Do NOT hallucinate missing details.
- Preserve all citations EXACTLY as provided (e.g., [source: filename.pdf]).
- If information is missing or unclear, explicitly state: "Not mentioned in the document."

LENGTH:
- Target length: 200–350 words.
- If the document is short, produce a shorter summary without adding filler.

OUTPUT FORMAT (FOLLOW EXACTLY):

##  Key Points
- List 4–6 concrete, factual points taken directly from the document.
- Each bullet must represent an explicit statement from the text.

##  Overview
- A short paragraph (3–5 sentences) explaining what the document is about.
- Use simple language; simplify technical concepts if present.

##  Additional Details
- Include important supporting details, definitions, or explanations mentioned in the document.
- Do NOT repeat the Key Points verbatim.

## Missing or Unclear Information
- List any important aspects that are NOT mentioned or are unclear in the document.
- If nothing is missing, write: "No missing or unclear information identified."

##  Sources
- List ALL sources exactly as provided in the document.
- Do NOT modify source names or formats.

DOCUMENT CONTENT:
{context}

Return ONLY the formatted summary above. Do not include explanations or extra text.
"""
)

def extract_sources(text: str) -> list:
    """
    Extract [source: ...] citations from text
    """
    pattern = r'\[source:\s*([^\]]+)\]'
    sources = re.findall(pattern, text)
    return list(set(sources))


def summarize_context(context: str) -> str:
    """
    Summarize document context while preserving sources
    """
    if not context or not context.strip():
        return "No content to summarize."

    try:
        sources = extract_sources(context)
        print(f"[INFO] Summary using sources: {sources}")

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3
        )

        chain = summary_prompt | llm

        response = chain.invoke(
            {"context": context}
        )

        final_answer = str(response.content)
        
        if sources:
            if "[source:" not in final_answer:
                sources_text = "\n\n**Sources:**\n" + "\n".join([f"- {source}" for source in sources])
                final_answer += sources_text
        
        return final_answer
        
    except Exception as e:
        print(f"[Error] Summarization failed: {e}")
        import traceback
        traceback.print_exc()
        return f"Error generating summary: {str(e)}"