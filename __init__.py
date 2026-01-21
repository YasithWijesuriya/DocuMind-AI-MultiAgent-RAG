# agents/__init__.py

from agents.ingestion_agent import ingest_document
from agents.retrieval_agent import retrieve_relevant_chunks
from agents.router_agent import route_question
from agents.summary_agent import summarize_context
from agents.compare_agent import compare_documents
from agents.synthesis_agent import synthesize_answer
from agents.validator_agent import validate_answer

# Optional: This defines what gets imported when someone uses "from agents import *"
__all__ = [
    "ingest_document",
    "retrieve_relevant_chunks",
    "route_question",
    "summarize_context",
    "compare_documents",
    "synthesize_answer",
    "validate_answer",
]