from config import OPENAI_MODEL, OPENAI_TEMPERATURE
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

validator_prompt = ChatPromptTemplate.from_template(
    """You are a validator agent in a multi-agent document analysis system.

Your role:
Critically evaluate the FINAL synthesized answer using ONLY the provided evidence.

STRICT RULES:
- Use ONLY the evidence provided
- Do NOT add new information
- Do NOT infer missing details
- Do NOT assume intent or context
- Do NOT rewrite the answer
- Do NOT hallucinate facts or sources
- Be objective and precise
- Use clear, professional academic language

CHECK FOR THE FOLLOWING:
- Hallucinations (claims not supported by evidence)
- Logical inconsistencies or contradictions
- Missing important points that ARE present in the evidence
- Overconfident or misleading wording
- Incorrect or fabricated citations
- Claims that exceed what the evidence explicitly states

EVALUATION GUIDELINES:
- If ALL claims in the final answer are directly supported by the evidence
  AND no important evidence-based points are missing → PASS
- If ANY unsupported, misleading, or contradictory claims exist → FAIL

FINAL ANSWER TO VALIDATE:
{final_answer}

EVIDENCE:
{evidence}

RESPONSE FORMAT (MANDATORY):

Validation Status: PASS or FAIL

Issues:
- List each issue clearly and concisely
- If there are no issues, write: None

Suggestions:
- Provide improvement suggestions ONLY if Validation Status is FAIL
- Suggestions must be based strictly on the provided evidence
- If no suggestions are needed, write: None
""")

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
