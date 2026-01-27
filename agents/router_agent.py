from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


ROUTES = ["retrieval", "summary", "compare", "expert"]

router_prompt = ChatPromptTemplate.from_template(
"""
You are a router agent in a multi-agent system.

Your task:
Analyze the user's question and determine which specialized agent is best suited to answer it.

Agent options:
1. retrieval_agent: Factual questions answered directly from document content.
2. summary_agent: Questions requiring a concise summary of document content.
3. compare_agent: Questions that involve comparing information across multiple documents.
4. expert_agent: Questions requiring deep explanation, interpretation, or reasoning beyond basic facts.

Instructions:
- Respond with ONLY one word from this list: retrieval, summary, compare, expert.
- Do NOT explain your choice, provide context, or add extra text.
- Base your choice solely on the content and type of the question.

User question:
{question}

Return your answer as a single word.
"""
)

def route_question(question: str) -> str:
    """
    Decide which agent should handle the user question
    """

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2
    )

    chain = router_prompt | llm  #file://./learn.md

    response = chain.invoke(  #file://./learn.md
        {"question": question}  
    )                      

    route = response.content.strip().lower()

    if route not in ROUTES:
        raise ValueError(f"Invalid route returned: {route}")

    return route
