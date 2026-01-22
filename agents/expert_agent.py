from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import re

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
- PRESERVE all [source: ...] citations from the provided content
- Add citations like [source: document_name] when referring to information

Document content:
{context}

User question:
{question}

Return:
- A clear expert explanation
- Any important implications or considerations
- Clearly state uncertainties if present
- Include [source: document_name] citations
"""
)

def extract_sources(text: str) -> list:
    """
    Extract [source: ...] citations from text
    """
    pattern = r'\[source:\s*([^\]]+)\]'
    sources = re.findall(pattern, text)
    return list(set(sources))


def expert_analysis(context: str, question: str) -> str:
    """
    Provide expert-level analysis of document content
    """
    try:
        sources = extract_sources(context)
        print(f"[INFO] Expert analysis using sources: {sources}")

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2
        )

        chain = expert_prompt | llm 

        response = chain.invoke(
            {
                "context": context,
                "question": question
            }
        )

        final_answer = str(response.content)
        
        if sources:
            if "[source:" not in final_answer:
                sources_text = "\n\n**Sources:**\n" + "\n".join([f"- {source}" for source in sources])
                final_answer += sources_text
        
        return final_answer
        
    except Exception as e:
        print(f"[Error] Expert analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return "An error occurred while processing the expert analysis."