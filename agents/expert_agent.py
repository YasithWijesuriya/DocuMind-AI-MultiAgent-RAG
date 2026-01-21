from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

expert_prompt = ChatPromptTemplate.from_template(
"""
You are an expert analysis agent in a multi-agent document analysis system.

Your task:
Provide a deep, expert-level explanation or interpretation based ONLY on the given document content.

Rules:
- Do NOT add new facts
- Do NOT assume information not explicitly stated
- Reason only from the provided content
- Clearly explain implications, meaning, or significance
- If something is unclear or missing, say "Not mentioned in the documents"
- Use simple, professional language
- Do NOT hallucinate sources

Document content:
{context}

User question:
{question}

Return:
- A clear expert explanation
- Any important implications or considerations
- Clearly state uncertainties if present
"""
)

def expert_analysis(context: str, question: str) -> str:

    try:
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2
        )

        chain = expert_prompt | llm 

        response = chain.invoke(
            {
                "context": context,
                "question": question
            }
        )

        return str(response.content)
    except Exception as e:
        print(f"Error in expert_analysis: {e}")
        return "An error occurred while processing the expert analysis."