from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import re
from typing import Optional


class SynthesisOutput(BaseModel):
    """Structured output for synthesized answer"""
    direct_answer: str = Field(description="Direct answer to the user's question in 1-2 sentences")
    key_information: list[str] = Field(
        default_factory=list,
        description="List of all explicit facts from the provided outputs"
    )
    uncertainties: list[str] = Field(
        default_factory=list,
        description="Information that is explicitly stated as uncertain"
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="Information explicitly mentioned as missing"
    )
    additional_details: str = Field(
        default="",
        description="Optional additional context directly mentioned in outputs"
    )
    sources: list[str] = Field(
        default_factory=list,
        description="All unique source document names referenced"
    )


synthesis_prompt = ChatPromptTemplate.from_template(
    """
# **Answer Synthesis & Integration**

## **Your Goal**
Combine agent outputs into ONE clear, concise, professional answer with proper citations.

## **Citation Requirements**
Every claim MUST be cited:
- **Format**: `[source: document_name]`
- **Example**: "The IoT platform supports 1000+ devices. [source: IoT System Design.pdf]"
- **Multiple Sources**: List all supporting sources: `[source: Doc A.pdf, Doc B.pdf]`
- **Rule**: EVERY sentence MUST have a citation

## **Strict Synthesis Rules**
✓ Use ONLY information from agent outputs  
✓ Remove all duplication  
✓ Keep answer concise  
✓ Clearly state uncertainties  
✓ Every statement MUST end with `[source: document_name]`  
✗ Do NOT add new information  
✗ Do NOT contradict agent outputs  
✗ Do NOT hallucinate facts or dates  

---

## **Agent Outputs**
{agent_outputs}

---

## **Required Output**

### **1. Direct Answer**
1-2 sentence answer with source

### **2. Key Information**
Factual points (each with source)

### **3. Source Documents**
All unique sources referenced

### **4. Uncertainties**
Any stated uncertainties

### **5. Missing Information**
Any explicitly mentioned gaps

### **6. Additional Context**
Relevant details (if any) with source
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


def synthesize_answer(agent_outputs: list[str]) -> SynthesisOutput:
    """
    Synthesize final answer from agent outputs with structured output
    
    Args:
        agent_outputs: List of outputs from different agents
        
    Returns:
        SynthesisOutput with structured synthesized answer (Pydantic model)
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
            temperature=0.2,
        )

        structured_llm = llm.with_structured_output(SynthesisOutput)

        combined_text = "\n\n".join(agent_outputs)

        chain = synthesis_prompt | structured_llm

        response = chain.invoke(
            {"agent_outputs": combined_text}
        )
        if isinstance(response, SynthesisOutput):
            return response
        return SynthesisOutput.model_validate(response)
        
    except Exception as e:
        print(f"[Error] Synthesis failed: {e}")
        import traceback
        traceback.print_exc()
        return SynthesisOutput(
            direct_answer="Error generating final answer.",
            key_information=[],
            uncertainties=[str(e)],
            missing_information=[]
        )


def format_synthesis_output(result: SynthesisOutput, sources: Optional[list[str]] = None) -> str:
    """
    Format SynthesisOutput into readable markdown
    
    Args:
        result: SynthesisOutput Pydantic model
        sources: Optional list of source citations
        
    Returns:
        Formatted string for display
    """
    output = "## Answer\n\n"
    
    output += f"{result.direct_answer}\n\n"
    
    if result.key_information:
        output += "### Key Information\n"
        for item in result.key_information:
            output += f"- {item}\n"
        output += "\n"
    
    if result.uncertainties:
        output += "### Uncertainties\n"
        for item in result.uncertainties:
            output += f"- {item}\n"
        output += "\n"
    
    if result.missing_information:
        output += "### Missing Information\n"
        for item in result.missing_information:
            output += f"- {item}\n"
        output += "\n"
    
    if result.additional_details:
        output += "### Additional Details\n"
        output += f"{result.additional_details}\n\n"
    
    if sources:
        output += "### Sources\n"
        for source in sources:
            output += f"- {source}\n"
    
    return output