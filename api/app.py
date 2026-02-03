import config 
import os
import json
import hashlib
import asyncio
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.datastructures import UploadFile
from pipelines.graph_nodes import memory_read_node, memory_write_node, rewrite_node, VercelFriendlyStore
from mangum import Mangum


store = VercelFriendlyStore("documind_memory.db")


def file_hash(path: str) -> str:
    """Generate file hash for thread ID"""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()


async def stream_response(question: str, file_paths: list[str], thread_id: str):
    """
    Stream NDJSON response (streaming text + metadata)
    
    Args:
        question: User question
        file_paths: List of uploaded file paths
        thread_id: Thread identifier for memory
        
    Yields:
        NDJSON formatted responses
    """
    from pipelines.docmind_pipeline import ask, get_route_type

    try:
        # Load conversation history
        state = {"thread_id": thread_id}
        state = memory_read_node(state)

        # Rewrite question
        state["question"] = question
        state = rewrite_node(state)
        rewritten_question = state.get("rewritten_question", question)

        # Determine route and auto-ingest setting
        route = get_route_type(rewritten_question)
        auto_ingest = route != "summary"

        # Run pipeline
        result = await asyncio.to_thread(
            ask,
            question=rewritten_question,
            docs=file_paths,
            auto_ingest=auto_ingest
        )

        # Save to memory
        state["original_question"] = question
        state["final_answer"] = result.get("final_answer", "")
        state = memory_write_node(state)

        # Stream response word by word
        final_answer = state.get("final_answer", "")
        
        if final_answer:
            words = final_answer.split()
            for i, word in enumerate(words):
                yield json.dumps({
                    "type": "text",
                    "content": word + " ",
                    "progress": int((i / len(words)) * 100)
                }) + "\n"
                await asyncio.sleep(0.01)  # Reduced for better UX

        # Final completion message
        yield json.dumps({
            "type": "complete",
            "content": final_answer,
            "validation": result.get("validation", {}),
            "route": result.get("route", "")
        }) + "\n"

    except Exception as e:
        import traceback
        traceback.print_exc()
        yield json.dumps({
            "type": "error",
            "content": str(e)
        }) + "\n"


async def ask_endpoint(request: Request):
    """
    Handle POST /ask request
    Expects: question (form field), files (file uploads)
    """
    try:
        form = await request.form()
        question = str(form.get("question", ""))
        
        if not question:
            return JSONResponse(
                {"error": "question field is required"}, 
                status_code=400
            )
        
        os.makedirs("/tmp", exist_ok=True)
        file_paths = []
        thread_ids = []

        # Extract uploaded files
        files = [v for v in form.values() if isinstance(v, UploadFile)]

        for f in files:
            filename = f.filename or "uploaded.pdf"
            path = os.path.join("/tmp", filename)
            
            content = await f.read()
            with open(path, "wb") as out:
                out.write(content)
            
            file_paths.append(path)
            tid = file_hash(path)
            thread_ids.append(tid)
            print(f"[INFO] File saved: {path}")

        # Combine thread IDs for consistent memory across files
        combined_thread_id = "_".join(thread_ids) if thread_ids else "default-thread"

        # Return streaming response
        return StreamingResponse(
            stream_response(question, file_paths, combined_thread_id),
            media_type="application/x-ndjson"
        )

    except Exception as e:
        print(f"[Error] Ask endpoint failed: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


async def health_endpoint(request: Request):
    """Health check endpoint"""
    return JSONResponse({
        "status": "ok",
        "service": "DocuMind",
        "version": "2.1"
    })


async def info_endpoint(request: Request):
    """API info endpoint"""
    return JSONResponse({
        "service": "DocuMind",
        "version": "2.1",
        "description": "Multi-agent document analysis system",
        "endpoints": {
            "POST /ask": "Analyze documents with streaming response",
            "GET /health": "Health check",
            "GET /info": "API information"
        }
    })

async def root_endpoint(request: Request):
    return JSONResponse({
        "message": "DocuMind API is running",
        "endpoints": ["/ask", "/health", "/info"]
    })

# Define routes
routes = [
    Route("/", root_endpoint, methods=["GET"]),
    Route("/ask", ask_endpoint, methods=["POST"]),
    Route("/health", health_endpoint, methods=["GET"]),
    Route("/info", info_endpoint, methods=["GET"]),
]

# Create Starlette app
app = Starlette(routes=routes)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # Add your Vercel domain here
        # "https://yourdomain.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Vercel handler
asgi_handler = Mangum(app)

def handler(event, context):
    return asgi_handler(event, context)



if __name__ == "__main__":
    import uvicorn
    # Local development
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")