from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

rewrite_prompt = ChatPromptTemplate.from_template(
    """You are a professional question rewriting agent for a document-based Q&A system.

Your goal is to rewrite the user's latest question so that it is:
1. Fully self-contained and understandable without prior context
2. Clear, precise, and unambiguous
3. Suitable for semantic search over documents

Rules:
- Only use the conversation history if necessary to resolve pronouns or references (e.g., "it", "this", "that", "they").
- If the question is already clear and standalone, return it unchanged.
- Do NOT introduce new information or content.
- Do NOT attempt to answer the question.
- Do NOT include explanations, reasoning, or extra text.
- Preserve the user's intent and meaning exactly.

Conversation history (for reference if needed):
{history}

User's latest question:
{question}

Rewritten standalone question:"""
) 

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
    print(f"History: {history_text}, Question: {question}")
    
    return str(response.content)