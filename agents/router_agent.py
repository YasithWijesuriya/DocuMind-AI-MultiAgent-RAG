from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from enum import Enum


class RouteType(str, Enum):
    RETRIEVAL = "retrieval"
    SUMMARY = "summary"
    COMPARE = "compare"
    EXPERT = "expert"


class RoutingDecision(BaseModel):
    """Structured output for routing decision"""
    route: RouteType = Field(description="Selected route: retrieval, summary, compare, or expert")
    reasoning: str = Field(description="Brief explanation for the routing decision")
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence in this routing decision (0-1)"
    )


ROUTES = [route.value for route in RouteType]

router_prompt = ChatPromptTemplate.from_template(
    """
# **Intelligent Query Router**

## **Your Purpose**
Analyze the user's question and route it to the most appropriate specialist agent.

## **Available Routes**

| Agent | Best For |
|-------|----------|
| **retrieval_agent** | Factual questions answered directly from documents |
| **summary_agent** | Questions requiring concise document summaries |
| **compare_agent** | Questions comparing information across multiple documents |
| **expert_agent** | Deep explanations, interpretation, or complex reasoning |

## **Routing Instructions**
✓ Choose ONLY one route based on question type  
✓ Provide brief reasoning  
✓ Rate confidence (0-1 scale)  
✗ Do NOT choose multiple routes  

---

## **User Question**
{question}

---

## **Required Output**

### **1. Routing Decision**
Select one agent route

### **2. Reasoning**
Brief explanation for this choice

### **3. Confidence Score**
0.0 to 1.0 (how certain you are)
"""
)



def route_question(question: str) -> str:
    """
    Decide which agent should handle the user question with structured output
    
    Args:
        question: User's question
        
    Returns:
        Route type (retrieval, summary, compare, expert)
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
    )

    structured_llm = llm.with_structured_output(RoutingDecision)
    chain = router_prompt | structured_llm

    response = chain.invoke({"question": question})

    if isinstance(response, RoutingDecision):
        result = response
    else:
        result = RoutingDecision.model_validate(response)

    route = result.route.value if isinstance(result.route, RouteType) else str(result.route).lower()

    if route not in ROUTES:
        print(f"[WARNING] Invalid route '{route}', defaulting to retrieval")
        return "retrieval"

    print(f"[ROUTER] Question routed to: {route} (confidence: {result.confidence:.1%})")
    print(f"[ROUTER] Reasoning: {result.reasoning}")

    return route



def get_routing_details(question: str) -> RoutingDecision:
    """
    Get full routing decision with reasoning and confidence
    
    Args:
        question: User's question
        
    Returns:
        RoutingDecision Pydantic model with all details
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
    )

    structured_llm = llm.with_structured_output(RoutingDecision)
    chain = router_prompt | structured_llm
    
    response = chain.invoke({"question": question})

    if isinstance(response, RoutingDecision):
        return response
    return RoutingDecision.model_validate(response)