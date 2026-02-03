from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """Structured output for answer validation"""
    status: str = Field(description="PASS or FAIL")
    issues: list[str] = Field(
        default_factory=list,
        description="List of identified issues"
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Improvement suggestions"
    )
    confidence_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence in validation (0-1)"
    )


validator_prompt = ChatPromptTemplate.from_template(
    """
# **Answer Validation & Quality Check**

## **Your Role**
Critically evaluate the final synthesized answer using ONLY provided evidence.

## **Validation Checklist**
- [ ] Hallucinations (claims not supported by evidence)
- [ ] Logical inconsistencies or contradictions
- [ ] Missing important evidence-based points
- [ ] Overconfident or misleading wording
- [ ] Incorrect or fabricated citations
- [ ] Claims exceeding what evidence states

## **Citation Validation**
✓ Every major claim has a `[source: document_name]` citation  
✓ All cited sources actually exist in evidence  
✓ No invented or fake source names  
✓ Citations match correct content  

## **Evaluation Criteria**

| Status | Condition |
|--------|-----------|
| **PASS** | All claims supported + citations correct + no important points missing |
| **FAIL** | Any unsupported claims OR incorrect citations OR contradictions |

## **Strict Rules**
✓ Use ONLY provided evidence  
✓ Be objective and precise  
✓ Use professional academic language  
✗ Do NOT add new information  
✗ Do NOT rewrite the answer  
✗ Do NOT hallucinate sources  

---

## **Final Answer to Validate**
{final_answer}

## **Evidence**
{evidence}

---

## **Required Output**

### **1. Validation Status**
PASS or FAIL

### **2. Issues Found**
Any problems identified (including citation errors)

### **3. Improvement Suggestions**
Recommended changes (if FAIL)

### **4. Confidence Score**
0.0 to 1.0 (validation confidence)
"""
)


def validate_answer(final_answer: str, evidence: str) -> ValidationResult:
    """
    Validate final answer against evidence with structured output
    
    Args:
        final_answer: Final synthesized answer to validate
        evidence: Source evidence to validate against
        
    Returns:
        ValidationResult with status, issues, and suggestions (Pydantic model)
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1
    )

    structured_llm = llm.with_structured_output(ValidationResult)

    chain = validator_prompt | structured_llm

    response = chain.invoke(
        {
            "final_answer": final_answer,
            "evidence": evidence
        }
    )
    if isinstance(response, ValidationResult):
        return response
    return ValidationResult.model_validate(response)

def format_validation_result(result: ValidationResult) -> str:
    """
    Format ValidationResult into readable text
    
    Args:
        result: ValidationResult Pydantic model
        
    Returns:
        Formatted string for display
    """
    output = "## Validation Report\n\n"
    
    status_emoji = "✔" if result.status == "PASS" else "❌"
    output += f"### Status: {status_emoji} {result.status}\n\n"
    
    output += f"**Confidence Score:** {result.confidence_score:.1%}\n\n"
    
    if result.issues:
        output += "### Issues Found\n"
        for issue in result.issues:
            output += f"- {issue}\n"
        output += "\n"
    else:
        output += "### Issues\nNo issues found ✔\n\n"
    
    if result.suggestions:
        output += "### Suggestions for Improvement\n"
        for suggestion in result.suggestions:
            output += f"- {suggestion}\n"
    else:
        if result.status == "FAIL":
            output += "### Suggestions\nNo specific suggestions available.\n"
    
    return output