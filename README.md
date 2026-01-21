
documind/
│
├── agents/
│
│   ├── ingestion_agent.py - split as chunks -> vector -> save pinecone
│   │
│   ├── retrieval_agent.py - User Question → Convert question(embedding) → Pinecone similarity search → Top-k relevant chunks → Return as context
│   │
│   ├── router_agent.py - Deciding which agent to send this to?
│   │
│   ├── summary_agent.py - Retrieved relevant chunks -> LLM summarizes -> Structured summary
│   │
│   ├── compare_agent.py - Retrieval Agent (doc A) | Retrieval Agent (doc B) -> Combine contexts -> Compare Agent->
Structured comparison
│   │
│   ├── synthesis_agent.py - Agent Outputs (texts) -> Normalize + merge -> LLM synthesizes -> Final Answer
│   │
│   ├── validator_agent.py - Validation Report -> (Optionally) improve answer
│   
│
├── config/
│   └── settings.py
│
├── data/
│   └── uploads/
│
├── main.py
└── .env

~FULL PIPELINE CONCEPT~

User Question
     ↓
Router Agent → decides which agent(s) to call
     ↓
Agents (Retrieval / Summary / Compare / Expert)
     ↓
Synthesis Agent → merge outputs
     ↓
Validator Agent → check quality & hallucinations
     ↓
Final Answer (returned to user)
