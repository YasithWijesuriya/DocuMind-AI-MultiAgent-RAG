from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class RewriteResult(BaseModel):
    """Structured output for question rewriting"""
    rewritten_question: str = Field(description="Standalone, self-contained question")
    is_follow_up: bool = Field(default=False, description="Whether this is a follow-up question")


rewrite_prompt = ChatPromptTemplate.from_template(
    """
# **Question Rewriting Service**

## **Your Objective**
Transform the user's question into a clear, standalone query suitable for document analysis.

## **Rewriting Rules**
✓ Make the question fully self-contained  
✓ Resolve pronouns and unclear references  
✓ Preserve user intent exactly  
✓ Keep the meaning precise and unambiguous  
✗ Do NOT introduce new information  
✗ Do NOT answer the question  
✗ Do NOT add reasoning or explanations  

---

## **Conversation History**
(Use only if necessary to resolve references)
{history}

## **User's Latest Question**
{question}

---

## **Required Output**

### **1. Rewritten Question**
Standalone, clear, and precise version

### **2. Follow-up Status**
Indicate if this is a follow-up question (true/false)
"""
)



def rewrite_question(history_text: str, question: str) -> str:
    """
    Rewrite question to be standalone using conversation history if needed
    
    Args:
        history_text: Previous conversation context
        question: Current question to rewrite
        
    Returns:
        Rewritten standalone question
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2
    )

    structured_llm = llm.with_structured_output(RewriteResult)
    chain = rewrite_prompt | structured_llm

    response = chain.invoke({
        "history": history_text,
        "question": question
    })
    if isinstance(response, RewriteResult):
        result = response
    else:
        result = RewriteResult.model_validate(response)
    
    print(f"[REWRITE] Original: {question}")
    print(f"[REWRITE] Rewritten: {result.rewritten_question}")
    print(f"[REWRITE] Is follow-up: {result.is_follow_up}")

   
    return result.rewritten_question