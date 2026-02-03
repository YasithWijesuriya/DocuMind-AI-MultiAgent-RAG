from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import re
from typing import Optional


class ExpertAnalysisResult(BaseModel):
    """Structured output for expert analysis"""
    analysis: str = Field(description="Deep expert-level explanation")
    implications: list[str] = Field(
        default_factory=list,
        description="Important implications"
    )
    uncertainties: list[str] = Field(
        default_factory=list,
        description="Areas of uncertainty"
    )
    sources:list[str]=Field(
        default_factory=list,
        description="All unique source document names referenced"
    )

expert_prompt = ChatPromptTemplate.from_template(
    """
# **Expert Analysis & Interpretation**

## **Your Role**
You are an expert analysis agent providing deep, authoritative explanations based ONLY on document content.

## **Citation Requirements**
Every claim MUST be followed by a citation:
- **Format**: `[source: document_name]`
- **Example**: "The system uses edge computing for real-time processing. [source: IoT Architecture.pdf]"
- **Rule**: EVERY sentence or key point MUST have a citation
- **Multiple Sources**: If supported by multiple chunks, cite all relevant sources

## **Strict Operational Rules**
✓ Reason only from provided content  
✓ Clearly explain implications and significance  
✓ Use simple, professional language  
✓ Every statement MUST end with `[source: document_name]`  
✗ Do NOT add new facts  
✗ Do NOT assume information  
✗ Do NOT hallucinate sources  

---

## **Document Content**
{context}

## **User Question**
{question}

---

## **Required Output**

### **1. Expert Explanation**
Deep analysis with citations after every statement

### **2. Key Implications**
Important implications or considerations (each with source)

### **3. Uncertainties**
Clearly state what is unclear or missing from documents

### **4. Source Documents**
All unique source document names referenced
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


def expert_analysis(context: str, question: str) -> ExpertAnalysisResult:
    """
    Provide expert-level analysis of document content with structured output
    
    Args:
        context: Document content with sources
        question: User's question
        
    Returns:
        ExpertAnalysisResult with structured analysis (Pydantic model)
    """
    try:
        sources = extract_sources(context)
        print(f"[INFO] Expert analysis using sources: {sources}")

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2
        )

        structured_llm = llm.with_structured_output(ExpertAnalysisResult)

        chain = expert_prompt | structured_llm

        response = chain.invoke(
            {
                "context": context,
                "question": question
            }
        )

        if isinstance(response, ExpertAnalysisResult):
            return response
        return ExpertAnalysisResult.model_validate(response)
        
    except Exception as e:
        print(f"[Error] Expert analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return ExpertAnalysisResult(
            analysis="An error occurred while processing the expert analysis.",
            implications=[],
            uncertainties=[str(e)]
        )


def format_expert_result(result: ExpertAnalysisResult, sources:Optional[list[str]] = None) -> str:
    """
    Format ExpertAnalysisResult into readable text
    
    Args:
        result: ExpertAnalysisResult Pydantic model
        sources: Optional list of source citations
        
    Returns:
        Formatted string for display
    """
    output = "## Expert Analysis\n\n"
    
    output += "### Analysis\n"
    output += f"{result.analysis}\n\n"
    
    if result.implications:
        output += "### Implications\n"
        for item in result.implications:
            output += f"- {item}\n"
        output += "\n"
    
    if result.uncertainties:
        output += "### Uncertainties\n"
        for item in result.uncertainties:
            output += f"- {item}\n"
        output += "\n"
    
    if sources:
        output += "### Sources\n"
        for source in sources:
            output += f"- {source}\n"
    
    return output