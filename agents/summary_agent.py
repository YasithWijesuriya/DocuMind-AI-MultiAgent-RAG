from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import re

summary_prompt = ChatPromptTemplate.from_template(
"""
You are a document summarization agent in a RAG system.

Your task:
Generate a clear, concise, and professional summary of the provided document chunks.

STRICT RULES:
- Use ONLY the information explicitly provided in the document chunks below.
- Do NOT add new information, context, or facts beyond what is given.
- Do NOT assume or infer missing information.
- Do NOT hallucinate any details, statistics, dates, locations, or topics.
- Do NOT mention topics not present in the provided chunks.
- Use simple and clear language; if the content is technical, explain it clearly.
- Keep the summary between 300-400 words.
- PRESERVE all citations exactly as provided (e.g., [source: ...]).
- If information seems incomplete, explicitly state "Additional details not provided in the retrieved document sections."
- Focus on main points; avoid unnecessary details.
- If the retrieved content is minimal or fragmented, create a summary based ONLY on what you can see.

VALIDATION CHECKLIST:
Before returning your answer, verify:
1. ✓ Did I only use information from the chunks provided?
2. ✓ Are all claims explicitly supported by the text?
3. ✓ Did I avoid inferring or assuming missing information?
4. ✓ Are all sources cited correctly?

Document chunks to summarize:
{context}

Return a summary following the format above.
"""
)

anti_hallucination_prompt = ChatPromptTemplate.from_template(
"""
You are a fact-checking agent. Your job is to verify that a summary ONLY contains information from the provided source text.

TASK:
1. Read the source text carefully
2. Read the summary
3. Check if every claim in the summary is directly supported by the source text
4. If you find any unsupported claims, flag them as HALLUCINATIONS

SOURCE TEXT:
{context}

SUMMARY TO CHECK:
{summary}

RESPONSE FORMAT:
Status: [OK or HALLUCINATION_DETECTED]
Issues: [List any unsupported claims, or "None"]
Corrected Summary: [If issues found, provide corrected version. Otherwise, return original]
"""
)


def extract_sources(text: str) -> list:
    """
    Extract [source: ...] citations from text
    """
    pattern = r'\[source:\s*([^\]]+)\]'
    sources = re.findall(pattern, text)
    return list(set(sources))


def check_hallucinations(context: str, summary: str) -> dict:
    """
    Use LLM to verify that summary doesn't hallucinate
    
    Returns:
        dict with keys: status, issues, corrected_summary
    """
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1  
        )
        
        chain = anti_hallucination_prompt | llm
        
        response = chain.invoke({
            "context": context,
            "summary": summary
        })
        
        content = str(response.content)
        
        result = {
            "status": "OK",
            "issues": [],
            "corrected_summary": summary
        }
        
        if "HALLUCINATION_DETECTED" in content.upper():
            result["status"] = "HALLUCINATION_DETECTED"
            print("[WARNING] Hallucination detected in summary!")
        
        print(f"[INFO] Hallucination check result: {result['status']}")
        return result
        
    except Exception as e:
        print(f"[Error] Hallucination check failed: {e}")
        return {
            "status": "CHECK_FAILED",
            "issues": [str(e)],
            "corrected_summary": summary
        }


def summarize_context(context: str, enable_anti_hallucination: bool = True) -> str:
    """
    Summarize document context while preserving sources and preventing hallucinations
    
    Args:
        context: The document chunks/text to summarize (should be pre-filtered relevant chunks)
        enable_anti_hallucination: If True, verify summary against hallucinations
    """
    if not context or not context.strip():
        return "No content to summarize."

    try:
        sources = extract_sources(context)
        print(f"[INFO] Summarizing with sources: {sources}")

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3
        )

        chain = summary_prompt | llm

        response = chain.invoke(
            {"context": context}
        )

        final_answer = str(response.content)
        
        if enable_anti_hallucination:
            print("[INFO] Running anti-hallucination check...")
            check_result = check_hallucinations(context, final_answer)
            
            if check_result["status"] == "HALLUCINATION_DETECTED":
                print("[WARNING] Hallucinations detected! Using corrected version.")
                final_answer = check_result["corrected_summary"]
        
        # Add sources section if not already present
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