from typing import TypedDict, List

class DocuMindState(TypedDict):
    question: str
    route: str
    docs: List[str]
    agent_outputs: List[str]
    final_answer: str
    validation: dict
