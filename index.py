import sys
import os


for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 
            'http_proxy', 'https_proxy', 'all_proxy', 'no_proxy', 'NO_PROXY']:
    os.environ.pop(key, None)

print("[INFO] Proxy environment cleared")

# Import config
import config

import json
import hashlib
import asyncio
from pathlib import Path
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.datastructures import UploadFile
from starlette.staticfiles import StaticFiles
from pipelines.graph_nodes import memory_read_node, memory_write_node, rewrite_node
from mangum import Mangum

# DEBUG: Print file structure
print("\n" + "="*60)
print("[DEBUG] CHECKING FILE STRUCTURE")
print("="*60)

current_dir = Path(__file__).parent
print(f"[DEBUG] Current file location: {__file__}")
print(f"[DEBUG] Current directory: {current_dir}")
print(f"[DEBUG] Current directory (absolute): {current_dir.absolute()}")

print(f"\n[DEBUG] Contents of {current_dir}:")
try:
    for item in sorted(current_dir.iterdir()):
        if item.is_dir():
            print(f"  [DIR] {item.name}/")
        else:
            print(f"  [FILE] {item.name}")
except Exception as e:
    print(f"  [ERROR] Error listing directory: {e}")

# Check documind-frontend
frontend_dir = current_dir / "documind-frontend"
print(f"\n[DEBUG] Checking documind-frontend at: {frontend_dir}")
print(f"[DEBUG] Exists: {frontend_dir.exists()}")

if frontend_dir.exists():
    print(f"[DEBUG] Contents of documind-frontend/:")
    try:
        for item in sorted(frontend_dir.iterdir()):
            if item.is_dir():
                print(f"  [DIR] {item.name}/")
            else:
                print(f"  [FILE] {item.name}")
    except Exception as e:
        print(f"  [ERROR] Error listing directory: {e}")
    
    # Check dist folder
    dist_dir = frontend_dir / "dist"
    print(f"\n[DEBUG] Checking dist at: {dist_dir}")
    print(f"[DEBUG] Exists: {dist_dir.exists()}")
    
    if dist_dir.exists():
        print(f"[DEBUG] Contents of documind-frontend/dist/:")
        try:
            for item in sorted(dist_dir.iterdir())[:10]:  # Show first 10 items
                if item.is_dir():
                    print(f"  [DIR] {item.name}/")
                else:
                    print(f"  [FILE] {item.name}")
        except Exception as e:
            print(f"  [ERROR] Error listing directory: {e}")
else:
    print(f"[DEBUG] documind-frontend folder NOT found!")

print("="*60 + "\n")


def file_hash(path: str) -> str:
    """Generate file hash for thread ID"""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()


async def stream_response(question: str, file_paths: list[str], thread_id: str):
    """
    Stream NDJSON response word-by-word

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

        # Rewrite question using history
        state["question"] = question
        state = rewrite_node(state)
        rewritten_question = state.get("rewritten_question", question)

        # Determine auto-ingest
        route = get_route_type(rewritten_question)
        auto_ingest = route != "summary"

        # Run pipeline (blocking → run in thread)
        result = await asyncio.to_thread(
            ask,
            question=rewritten_question,
            docs=file_paths,
            auto_ingest=auto_ingest
        )

        # Save to memory
        state["original_question"] = question
        state["final_answer"] = result.get("final_answer", "")
        memory_write_node(state)

        # Stream the final answer word by word
        final_answer = result.get("final_answer", "")

        if final_answer:
            words = final_answer.split()
            total = len(words)
            for i, word in enumerate(words):
                yield json.dumps({
                    "type": "text",
                    "content": word + " ",
                    "progress": int((i / total) * 100)
                }) + "\n"
                await asyncio.sleep(0.01)

        # Final complete event
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
    """Handle POST /ask"""
    try:
        form = await request.form()
        question = str(form.get("question", ""))

        if not question:
            return JSONResponse({"error": "question field is required"}, status_code=400)

        os.makedirs("/tmp", exist_ok=True)
        file_paths = []
        thread_ids = []

        files = [v for v in form.values() if isinstance(v, UploadFile)]

        for f in files:
            filename = f.filename or "uploaded.pdf"
            clean_name = filename.replace(" ", "_").replace("\\", "_")
            path = os.path.join("/tmp", clean_name)

            content = await f.read()
            with open(path, "wb") as out:
                out.write(content)

            file_paths.append(path)
            thread_ids.append(file_hash(path))
            print(f"[INFO] File saved: {path}")

        if not file_paths:
            return JSONResponse({"error": "No files uploaded"}, status_code=400)

        combined_thread_id = "_".join(thread_ids)

        return StreamingResponse(
            stream_response(question, file_paths, combined_thread_id),
            media_type="application/x-ndjson"
        )

    except Exception as e:
        print(f"[ERROR] Ask endpoint failed: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


async def health_endpoint(request: Request):
    return JSONResponse({"status": "ok", "service": "DocuMind", "version": "2.1"})


async def info_endpoint(request: Request):
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


# Routes
routes = [
    Route("/ask", ask_endpoint, methods=["POST"]),
    Route("/health", health_endpoint, methods=["GET"]),
    Route("/info", info_endpoint, methods=["GET"]),
]

app = Starlette(routes=routes)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "*",  
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#! SERVE REACT FRONTEND FROM documind-frontend/dist/
static_path = Path(__file__).parent / "documind-frontend" / "dist"

print(f"[INFO] Looking for static files at: {static_path}")
print(f"[INFO] Path exists: {static_path.exists()}")

if static_path.exists():
    print(f"[INFO] Serving React frontend from {static_path}")
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
else:
    print(f"[ERROR] Static files NOT found at {static_path}")
    print(f"[ERROR] dist/ folder is missing - React UI will not be served")
    print(f"[ERROR] Only API endpoints will work: /ask, /health, /info")


try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    pass

if __name__ == "__main__":
    import uvicorn
    # Get PORT from environment variable, default to 8000
    port = int(os.getenv("PORT", "8000"))
    print(f"[INFO] Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")