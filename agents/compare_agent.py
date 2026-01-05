from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

compare_prompt = ChatPromptTemplate.from_template(
     """
        You are a document comparison agent.

        Your task:
        Compare the following two document contents.

        Rules:
        - Do NOT add new information
        - Compare ONLY based on the given content
        - Be clear and structured
        - If information is missing, say "Not mentioned"

        Document A:
        {context_a}

        Document B:
        {context_b}

        Return the comparison in this structure:

        Similarities:
        - ...

        Differences:
        - Document A:
        - ...
        - Document B:
        - ...
    """
)

def compare_documents(context_a: str, context_b: str) -> str:

    llm = ChatOpenAI(
        temperature=0.3
    )

    chain = compare_prompt | llm

    response = chain.invoke(
        {
            "context_a": context_a,
            "context_b": context_b
        }
    )

    return str(response.content)