from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

rewrite_prompt = ChatPromptTemplate.from_template(
    """
    You are a question rewriting agent.

    Rewrite the user's question using conversation history
    so it is clear and self-contained.

    Conversation history:
    {history}

    User question:
    {question}

    Return only the rewritten question.
""")

llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2
    )

chain = rewrite_prompt | llm

def rewrite_question(history_text: str, question: str) -> str:

    response = chain.invoke({
        "history": history_text,
        "question": question
    })
    return str(response.content)