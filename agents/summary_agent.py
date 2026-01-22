from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import re

summary_prompt = ChatPromptTemplate.from_template(
    """
You are a document summarization agent.

Your task:
Summarize the following document content clearly and concisely.

Rules:
- Do NOT add new information
- Do NOT assume facts
- Use simple, clear language
- If the content is technical, explain it simply
- Keep summary to 300-400 words max
- PRESERVE all [source: ...] citations from the content
- Add citations like [source: document_name] when appropriate

Document content:
{context}

Return a structured summary with key points and citations.
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