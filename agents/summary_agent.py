from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import re
from typing import Optional


class SummaryResult(BaseModel):
    """Structured output for summary generation"""
    summary_text: str = Field(description="Concise summary of document (300-400 words)")
    key_points: list[str] = Field(
        default_factory=list,
        description="Main key points from the document"
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="Any information mentioned as missing or unclear"
    )
    sources: list[str] = Field(
        default_factory=list,
        description="All unique source document names referenced"
    )



summary_prompt = ChatPromptTemplate.from_template(
    """
# **Document Summarization**

## **Your Task**
Generate a clear, concise, professional summary of provided document chunks with full citations.

## **Citation Requirements**
Every claim MUST include a citation:
- **Format**: `[source: document_name]`
- **Example**: "IoT devices communicate using MQTT protocol. [source: Introduction to IoT.pdf]"
- **Rule**: EVERY sentence MUST have a citation
- **Multiple Sources**: Use comma-separated list if applicable

## **Strict Quality Rules**
✓ Use ONLY information explicitly in chunks  
✓ Keep summary 300-400 words  
✓ Use simple, clear language  
✓ Every statement MUST end with `[source: document_name]`  
✗ Do NOT add facts beyond what's given  
✗ Do NOT assume or infer information  
✗ Do NOT hallucinate details, statistics, or dates  
✗ Do NOT mention topics not in chunks  

---

## **Document Chunks**
{context}

---

## **Required Output**

### **1. Comprehensive Summary**
300-400 words with citations after every statement

### **2. Key Points**
Main points (each with source citation)

### **3. Source Documents**
All unique source names found

### **4. Missing Information**
Any gaps or incomplete information noted in documents
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

RESPONSE:
Respond with "VALID" if all claims are supported, or list any unsupported claims found.
"""
)


def extract_sources(text: str) -> list[str]:
    """
    Extract [source: ...] citations from text
    
    Args:
        text: Text containing source citations
        
    Returns:
        List of unique sources
    """
    pattern = r'\[source:\s*([^\]]+)\]'
    sources = re.findall(pattern, text)
    return list(set(sources))



def normalize_llm_content(content) -> str:
    """
    Normalize LangChain LLM content into a string
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, str):
                texts.append(item)
            elif isinstance(item, dict) and "text" in item:
                #! “If item is a dictionary AND it contains a text field…”
                texts.append(str(item["text"]))
        return " ".join(texts)

    return str(content)


def check_hallucinations(context: str, summary: str) -> dict:
    """
    Use LLM to verify that summary doesn't hallucinate
    
    Args:
        context: Original document context
        summary: Generated summary to check
        
    Returns:
        Dictionary with status and corrected_summary
    """
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
        )
        
        chain = anti_hallucination_prompt | llm
        
        response = chain.invoke({
            "context": context,
            "summary": summary
        })
        
        raw_content = response.content if hasattr(response, 'content') else response

        content = normalize_llm_content(raw_content)
        
        result = {
            "status": "VALID",
            "corrected_summary": summary
        }
        if "VALID" not in content.upper():
            result["status"] = "HALLUCINATION_DETECTED"
            print("[WARNING] Hallucination detected in summary!")
        
        print(f"[INFO] Hallucination check result: {result['status']}")
        return result
        
    except Exception as e:
        print(f"[Error] Hallucination check failed: {e}")
        return {
            "status": "CHECK_FAILED",
            "corrected_summary": summary
        }


def summarize_context(context: str, enable_anti_hallucination: bool = True) -> SummaryResult:
    """
    Summarize document context with structured output
    
    Args:
        context: The document chunks/text to summarize
        enable_anti_hallucination: If True, verify summary against hallucinations
        
    Returns:
        SummaryResult with structured summary (Pydantic model)
    """
    if not context or not context.strip():
        return SummaryResult(
            summary_text="No content to summarize.",
            key_points=[],
            missing_information=[]
        )

    try:
        sources = extract_sources(context)
        print(f"[INFO] Summarizing with sources: {sources}")

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
        )

        structured_llm = llm.with_structured_output(SummaryResult)

        chain = summary_prompt | structured_llm

        response = chain.invoke(
            {"context": context}
        )

        if isinstance(response, SummaryResult):
            summary_result = response
        else:
            raise TypeError("Expected SummaryResult, got something else")

        if enable_anti_hallucination:
            print("[INFO] Running anti-hallucination check...")
            check_result = check_hallucinations(context, summary_result.summary_text)
            
            if check_result["status"] == "HALLUCINATION_DETECTED":
                print("[WARNING] Hallucinations detected!")
        
        return summary_result
        
    except Exception as e:
        print(f"[Error] Summarization failed: {e}")
        import traceback
        traceback.print_exc()
        return SummaryResult(
            summary_text=f"Error generating summary: {str(e)}",
            key_points=[],
            missing_information=[str(e)]
        )


def format_summary_result(result: SummaryResult, sources: Optional[list[str]] = None) -> str:
    """
    Format SummaryResult into readable text
    
    Args:
        result: SummaryResult Pydantic model
        sources: Optional list of source citations
        
    Returns:
        Formatted string for display
    """
    output = "## Document Summary\n\n"
    
    output += "### Summary\n"
    output += f"{result.summary_text}\n\n"
    
    if result.key_points:
        output += "### Key Points\n"
        for point in result.key_points:
            output += f"- {point}\n"
        output += "\n"
    
    if result.missing_information:
        output += "### Missing Information\n"
        for item in result.missing_information:
            output += f"- {item}\n"
        output += "\n"
    
    if sources:
        output += "### Sources\n"
        for source in sources:
            output += f"- {source}\n"
    
    return output