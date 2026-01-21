from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

summary_prompt = ChatPromptTemplate.from_template(
    """
You are a document summarization agent.

Your task:
Summarize the following document content clearly and concisely.

Rules:
- Do NOT add new information
- Do NOT assume facts
- Use simple, clear language
- If the content is technical, explain it simply

Document content:
{context}

Return a structured summary with bullet points.
"""
)

def summarize_context(context: str) -> str:

    llm = ChatOpenAI(
        model="gpt-4",
        model_kwargs={"temperature": 0.3} 
    )

    chain = summary_prompt | llm # see : file://./learn.md

    response = chain.invoke(
        {"context": context}
    )

    return str(response.content)