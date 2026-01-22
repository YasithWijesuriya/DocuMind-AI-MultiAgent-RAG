import os
import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pipelines.docmind_pipeline import ask,get_route_type
import asyncio
import hashlib

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        'http://localhost:5173',
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def file_hash(path: str) -> str:
    """Generate file hash"""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()


async def stream_response(question: str, file_paths: list[str]):
    """
    Stream the response word by word for real-time effect
    """
    try:
        route = get_route_type(question)
        print(f"[INFO] Route: {route}")
        
        auto_ingest = route != "summary"
        print(f"[INFO] Auto-ingest: {auto_ingest}")
        
        # Run pipeline
        result = ask(
            question=question,
            docs=file_paths,
            auto_ingest=auto_ingest
        )

        final_answer = result.get("final_answer", "")
        
        if final_answer:
            words = final_answer.split()
            for i, word in enumerate(words):
                # Send word with space
                chunk = word + " "
                
                yield json.dumps({
                    "type": "text",
                    "content": chunk,
                    "progress": int((i / len(words)) * 100)
                }) + "\n"
                
                # Add small delay for typing effect
                await asyncio.sleep(0.02)
        
        # Send final result
        yield json.dumps({
            "type": "complete",
            "content": final_answer,
            "validation": result.get("validation")
        }) + "\n"

    except Exception as e:
        print(f"[Error] Stream error: {e}")
        import traceback
        traceback.print_exc()
        
        yield json.dumps({
            "type": "error",
            "content": str(e)
        }) + "\n"


@app.post("/ask")
async def ask_api(
    question: str = Form(...),
    files: list[UploadFile] = File(default=[])
):
    """
    Main API endpoint - returns streaming response
    
    Client receives chunks of data as they arrive
    """
    os.makedirs("temp", exist_ok=True)

    file_paths = []

    # Save files
    for f in files:
        filename = f.filename or "uploaded.pdf"
        path = os.path.join("temp", filename)
        
        with open(path, "wb") as out:
            content = await f.read()
            out.write(content)
        
        file_paths.append(path)
        print(f"[INFO] File saved: {path}")

    return StreamingResponse(
        stream_response(question, file_paths),
        media_type="application/x-ndjson"
    )


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "DocuMind"}