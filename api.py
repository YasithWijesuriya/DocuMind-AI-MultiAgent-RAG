import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pipelines.docmind_pipeline import ask
from agents.ingestion_agent import ingest_document
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask_endpoint(
    files: List[UploadFile] = File(...),
    question: str = Form(...)
):
    docs = []

    # Read uploaded files
    for file in files:
        try:
            if file.filename.lower().endswith(".pdf"):
                # Save temp file
                temp_path = f"temp_{file.filename}"
                with open(temp_path, "wb") as f:
                    f.write(await file.read())
                ingest_document(temp_path)  # Pinecone ingestion
                docs.append(temp_path)  # store path
            else:
                content = (await file.read()).decode("utf-8")
                docs.append(content)
        except Exception as e:
            return {"error": f"Error reading file {file.filename}: {str(e)}"}

    if len(docs) == 0:
        return {"error": "No documents provided."}

    try:
        response = ask(question, docs)
        return response
    except Exception as e:
        return {"error": str(e)}
