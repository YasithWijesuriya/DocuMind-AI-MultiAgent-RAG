# DocuMind-AI: Multi-Agent Agentic-RAG with LangGraph

DocuMind-AI is a state-of-the-art Retrieval-Augmented Generation (RAG) system built on a Stateful Multi-Agent Architecture using LangGraph. Unlike traditional linear pipelines, DocuMind-AI employs a sophisticated graph-based workflow that manages memory, rewrites queries for precision, and dynamically routes tasks to specialized agents.

## System Workflow (The Graph)
The entire logic is orchestrated via a StateGraph, ensuring seamless data flow between agents while maintaining conversation history.

graph TD

    Start((START)) --> MR[Memory Read]
    MR --> RW[Query Rewriter]
    RW --> Router{Router Decision}

    Router -- "retrieval / summary / expert" --> RA[Retrieval Agent]
    Router -- "compare" --> CA[Compare Agent]
    
    RA --> SA[Synthesis Agent]
    CA --> SA
    
    SA --> VA[Validator Agent]
    VA --> MW[Memory Write]
    MW --> End((END))


    
## 🛠 Nodes & Intelligence

Each node in the graph represents a specific state in the pipeline:

1. The Context Layer

     Memory Read (memory_read_node):
     Fetches the previous conversation state to provide "context-aware" answers.

     Query Rewrite (rewrite_node): If a user's question is vague, this agent rewrites it into a high-quality search query optimized for Vector DBs.
 
 2. The Decision Layer
 
     Router Node (router_node): Uses an LLM to decide the path.
     
          retrieval: Standard Q&A

          summary: High-level document overview.
          
          compare: Analyzing differences between multiple contexts.
     
3. The Execution Layer

       Retrieval Agent: Connects to Pinecone to fetch top-$k$ relevant chunks.

       Compare Agent: Merges multiple contexts for cross-document analysis.

4. Quality & Persistence

       Synthesis Agent: Merges all agent outputs into a natural, coherent response.

       Validator Agent: Acts as a critic. It checks for hallucinations and ensures the answer is grounded in the retrieved text.

       Memory Write: Stores the final interaction back into the system state for future turns.

## Key Tech Stack

     Framework: LangChain & LangGraph (for stateful multi-agent orchestration)

     Vector Database: Pinecone

     LLM: OpenAI (GPT-4o/gpt-4o-mini)

     Memory: Custom State Management

##  Installation & Usage

Clone & Install:

    git clone https://github.com/YasithWijesuriya/DocuMind-AI-MultiAgent-RAG.git
    pip install -r requirements.txt
Setup .env:

     OPENAI_API_KEY=your_openai_api_key
     PINECONE_API_KEY=your_pinecone_api_key
     PINECONE_ENVIRONMENT=your_environment_region
    
How to run:

    FrontEnd - npm run dev
    BackEnd  - uvicorn app:app --reload
     
