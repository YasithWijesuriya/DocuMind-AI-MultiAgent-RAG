from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.documents import Document

class DocuMindState(TypedDict, total=False):
    """
    State for the DocuMind graph
    All fields are optional (total=False)
    """
    question: Optional[str]
    original_question: Optional[str]
    rewritten_question: Optional[str]
    route: Optional[str]
    docs: List[Document]
    agent_outputs: List[str]
    final_answer: Optional[str]
    validation: Optional[Dict[str, Any]]
    conversation_history: List[Dict[str, str]]
    thread_id: Optional[str]