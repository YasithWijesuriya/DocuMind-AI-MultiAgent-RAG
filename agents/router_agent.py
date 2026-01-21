from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


ROUTES = ["retrieval", "summary", "compare", "expert"]

router_prompt = ChatPromptTemplate.from_template(
    """You are a router agent in a multi agent system.
    
    Your task :
    Analyze the user question and decide which specialized agent is best suited to answer it.

    1.retrieval_agent : factual questions answered from documents.
    2.summary_agent : questions requiring concise summaries of document content.
    3.compare_agent : questions that involve comparing information across multiple documents.
    4.expert_agent : deep explanation or interpretation.

    user question : {question}

    Respond with only one word  from this list:
    retrieval, summary, compare, expert
    
    """
)

def route_question(question: str) -> str:
    """
    Decide which agent should handle the user question
    """

    llm = ChatOpenAI(
        model="gpt-4",
        model_kwargs={"temperature": 0.2} 
    )

    chain = router_prompt | llm  #file://./learn.md

    response = chain.invoke(  #file://./learn.md
        {"question": question}  
    )                      

    route = response.content.strip().lower()

    if route not in ROUTES:
        raise ValueError(f"Invalid route returned: {route}")

    return route
