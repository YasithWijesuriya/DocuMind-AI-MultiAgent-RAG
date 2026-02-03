from typing import TypedDict, Optional, Dict, Any
from langchain_core.documents import Document
from pydantic import BaseModel, Field


class DocuMindState(TypedDict, total=False):
    """
    State for the DocuMind graph using TypedDict
    All fields are optional (total=False)
    
    Note: Using TypedDict instead of BaseModel for LangGraph compatibility
    """
    question: Optional[str]
    original_question: Optional[str]
    rewritten_question: Optional[str]
    route: Optional[str]
    docs: list[Document]
    agent_outputs: list[str]
    final_answer: Optional[str]
    validation: Optional[Dict[str, Any]]
    conversation_history: list[Dict[str, str]]
    thread_id: Optional[str]


class ChatMessage(BaseModel):
    """Represents a single message in conversation history"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[float] = Field(None, description="Optional timestamp")

    class Config:
        frozen = True  #! Make immutable


class ThreadMemory(BaseModel):
    """Represents conversation memory for a thread"""
    thread_id: str = Field(..., description="Unique thread identifier")
    messages: list[ChatMessage] = Field(default_factory=list, description="Conversation messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "thread_id": "abc123",
                "messages": [
                    {"role": "user", "content": "What is this document about?", "timestamp": 1234567890}
                ],
                "metadata": {"source": "web"}
            }
        }