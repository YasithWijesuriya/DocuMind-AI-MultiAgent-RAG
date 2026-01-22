from config import OPENAI_MODEL, OPENAI_TEMPERATURE
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

validator_prompt = ChatPromptTemplate.from_template(
    """
You are a validator agent in a multi-agent document analysis system.

Your task:
Evaluate the final answer based on the provided evidence.

Check for:
- Hallucinations (information not present in evidence)
- Logical inconsistencies
- Missing important points
- Overconfident or misleading statements

Final Answer:
{final_answer}

Evidence from agents / documents:
{evidence}

Return your response in this structure:

Validation Status: PASS or FAIL

Issues (if any):
- ...

Suggestions (if needed):
- ...
"""
)

def validate_answer(final_answer: str, evidence: str) -> dict:

    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=OPENAI_TEMPERATURE
    )

    chain = validator_prompt | llm # see : file://./learn.md

    response = chain.invoke(
        {
            "final_answer": final_answer,
            "evidence": evidence
        }
    )

    content = str(response.content)

    status = content.split("Validation Status:")[1].strip().split()[0]

    return {
        "status": status,
        "report": content
    }
