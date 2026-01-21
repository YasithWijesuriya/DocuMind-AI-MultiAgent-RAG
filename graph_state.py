from typing import TypedDict, List

class DocuMindState(TypedDict, total=False):
    question: str
    original_question: str
    route: str
    docs: List[str]
    agent_outputs: List[str]
    final_answer: str
    validation: dict
    conversation_history: List[dict]
    thread_id: str

