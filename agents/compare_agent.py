from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import httpx


class ComparisonResult(BaseModel):
    """Structured output for document comparison"""
    similarities: list[str] = Field(
        default_factory=list,
        description="List of similarities between documents"
    )
    differences_doc_a: list[str] = Field(
        default_factory=list,
        description="Unique points in Document A"
    )
    differences_doc_b: list[str] = Field(
        default_factory=list,
        description="Unique points in Document B"
    )
    sources: list[str] = Field(
        default_factory=list,
        description="All unique source document names referenced"
    )


compare_prompt = ChatPromptTemplate.from_template(
    """
# **Document Comparison Analysis**

## **Your Task**
Compare the following two document contents and provide structured, cited output with clear comparisons.

## **Citation Requirements**
Every point you make MUST be followed by a citation in this exact format:
- **Format**: `[source: document_name]`
- **Example**: "Both documents discuss cloud computing. [source: Doc A.pdf, Doc B.pdf]"
- **Similarities**: Cite BOTH documents `[source: Doc A.pdf, Doc B.pdf]`
- **Differences**: Cite only the relevant document `[source: Doc A.pdf]`

## **Strict Rules**
✓ Compare ONLY based on the given content  
✓ Every point MUST end with `[source: document_name]`  
✗ Do NOT add new information  
✗ Do NOT assume missing details  

---

## **Document A**
{context_a}

## **Document B**
{context_b}

---

## **Analysis Required**

### **1. Similarities**
Common points between both documents (cite both sources)

### **2. Unique to Document A**
Points only in Document A (cite source)

### **3. Unique to Document B**
Points only in Document B (cite source)

### **4. Source Documents**
List all unique source document names found
"""
)



def compare_documents(context_a: str, context_b: str) -> ComparisonResult:
    """
    Compare two documents using LLM with structured output
    
    Args:
        context_a: Content of first document
        context_b: Content of second document
        
    Returns:
        ComparisonResult with similarities and differences (Pydantic model)
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3
    )

    structured_llm = llm.with_structured_output(ComparisonResult)

    chain = compare_prompt | structured_llm

    response = chain.invoke(
        {
            "context_a": context_a,
            "context_b": context_b
        }
    )

    if isinstance(response, ComparisonResult):
        return response

    return ComparisonResult.model_validate(response)

def format_comparison_result(result: ComparisonResult) -> str:
    """
    Format ComparisonResult into readable text
    
    Args:
        result: ComparisonResult Pydantic model
        
    Returns:
        Formatted string for display
    """
    output = "## Document Comparison Results\n\n"
    
    output += "### Similarities\n"
    if result.similarities:
        for item in result.similarities:
            output += f"- {item}\n"
    else:
        output += "- No similarities found\n"
    
    output += "\n### Unique to Document A\n"
    if result.differences_doc_a:
        for item in result.differences_doc_a:
            output += f"- {item}\n"
    else:
        output += "- No unique points\n"
    
    output += "\n### Unique to Document B\n"
    if result.differences_doc_b:
        for item in result.differences_doc_b:
            output += f"- {item}\n"
    else:
        output += "- No unique points\n"
    
    return output