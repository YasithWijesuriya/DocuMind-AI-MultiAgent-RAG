# import os
# import json
# import hashlib
# import asyncio
# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse
# from pipelines.graph_nodes import SQLiteStore, memory_read_node, memory_write_node, rewrite_node
# from fastapi.responses import FileResponse
# import uvicorn
# import sys
# print("Python version:", sys.version)


# app = FastAPI()



# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "http://127.0.0.1:3000",
#         'http://localhost:5173',
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# store = SQLiteStore("documind_memory.db")


# def file_hash(path: str) -> str:
#     """Generate file hash (thread_id) based on file content"""
#     hasher = hashlib.sha256()
#     with open(path, "rb") as f:
#         hasher.update(f.read())
#     return hasher.hexdigest()


# async def stream_response(question: str, file_paths: list[str], thread_id: str):
#     from pipelines.docmind_pipeline import ask, get_route_type
#     try:
#         state = {"thread_id": thread_id}
#         state = memory_read_node(state)

#         state["question"] = question
#         state = rewrite_node(state)
#         rewritten_question = state.get("rewritten_question", question)

#         route = get_route_type(rewritten_question)
#         auto_ingest = route != "summary"

#         result = await asyncio.to_thread(
#             ask,
#             question=rewritten_question,
#             docs=file_paths,
#             auto_ingest=auto_ingest
#         )


#         state["original_question"] = question
#         state["final_answer"] = result.get("final_answer", "")
#         state = memory_write_node(state)

#         final_answer = state.get("final_answer", "")

#         if final_answer:
#             words = final_answer.split()
#             for i, word in enumerate(words):
#                 chunk = word + " "
#                 yield json.dumps({
#                     "type": "text",
#                     "content": chunk,
#                     "progress": int((i / len(words)) * 100)
#                 }) + "\n"
#                 await asyncio.sleep(0.02)

#         yield json.dumps({
#             "type": "complete",
#             "content": final_answer,
#             "validation": result.get("validation")
#         }) + "\n"

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         yield json.dumps({
#             "type": "error",
#             "content": str(e)
#         }) + "\n"



# @app.post("/ask")
# async def ask_api(
#     question: str = Form(...),
#     files: list[UploadFile] = File(default=[])
# ):
#     """
#     Main API endpoint - returns streaming response
#     """
#     os.makedirs("/tmp", exist_ok=True)


#     file_paths = []
#     thread_ids = []

#     # Save files & generate thread_id per file
#     for f in files:
#         filename = f.filename or "uploaded.pdf"
#         path = os.path.join("/tmp", filename)

#         with open(path, "wb") as out:
#             content = await f.read()
#             out.write(content)

#         file_paths.append(path)
#         tid = file_hash(path)  # generate thread_id from file content
#         thread_ids.append(tid)
#         print(f"[INFO] File saved: {path}, Thread ID: {tid}")

#     combined_thread_id = "_".join(thread_ids)

#     return StreamingResponse(
#         stream_response(question, file_paths, combined_thread_id),
#         media_type="application/x-ndjson"
#     )


# @app.get("/health")
# async def health():
#     """Health check endpoint"""
#     return {"status": "ok", "service": "DocuMind"}

# @app.get("/favicon.ico")
# async def favicon():
#     if os.path.exists("static/favicon.ico"):
#         return FileResponse("static/favicon.ico")
#     return {}  # empty JSON prevent 500



# @app.get("/")
# def root():
#     return {"message": "DOCMIND is running!"}

# # Example route to test memory read/write
# @app.get("/test-memory")
# def test_memory():
#     thread_id = "test-thread"
#     store.put(thread_id, "conversation", {"messages": [{"role": "user", "content": "Hello"}]})
#     data = store.get(thread_id, "conversation")
#     return {"thread_id": thread_id, "data": data}

# # Run locally
# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


import os
import json
import hashlib
import asyncio
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse, FileResponse
from starlette.datastructures import UploadFile
from pipelines.graph_nodes import SQLiteStore, memory_read_node, memory_write_node, rewrite_node

# Initialize SQLite store
store = SQLiteStore("documind_memory.db")


def file_hash(path: str) -> str:
    """Generate file hash (thread_id) based on file content"""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()


async def stream_response(question: str, file_paths: list[str], thread_id: str):
    """Generator for streaming NDJSON response"""
    from pipelines.docmind_pipeline import ask, get_route_type

    try:
        state = {"thread_id": thread_id}
        state = memory_read_node(state)

        state["question"] = question
        state = rewrite_node(state)
        rewritten_question = state.get("rewritten_question", question)

        route = get_route_type(rewritten_question)
        auto_ingest = route != "summary"

        result = await asyncio.to_thread(
            ask,
            question=rewritten_question,
            docs=file_paths,
            auto_ingest=auto_ingest
        )

        state["original_question"] = question
        state["final_answer"] = result.get("final_answer", "")
        state = memory_write_node(state)

        final_answer = state.get("final_answer", "")

        if final_answer:
            words = final_answer.split()
            for i, word in enumerate(words):
                chunk = word + " "
                yield json.dumps({
                    "type": "text",
                    "content": chunk,
                    "progress": int((i / len(words)) * 100)
                }) + "\n"
                await asyncio.sleep(0.02)

        # Final complete message
        yield json.dumps({
            "type": "complete",
            "content": final_answer,
            "validation": result.get("validation")
        }) + "\n"

    except Exception as e:
        import traceback
        traceback.print_exc()
        yield json.dumps({
            "type": "error",
            "content": str(e)
        }) + "\n"


async def ask_endpoint(request: Request):
    """Handle /ask POST request"""
    form = await request.form()
    question_raw = form.get("question", "")
    if not question_raw:
        return JSONResponse({"error": "question is required"}, status_code=400)
    question = str(question_raw)
    
    os.makedirs("/tmp", exist_ok=True)
    file_paths = []
    thread_ids = []

    # Extract UploadFile objects only
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

    combined_thread_id = "_".join(thread_ids) if thread_ids else "default-thread"

    return StreamingResponse(
        stream_response(question, file_paths, combined_thread_id),
        media_type="application/x-ndjson"
    )


async def health_endpoint(request: Request):
    return JSONResponse({"status": "ok", "service": "DocuMind"})


async def favicon_endpoint(request: Request):
    if os.path.exists("static/favicon.ico"):
        return FileResponse("static/favicon.ico")
    return JSONResponse({})


async def root_endpoint(request: Request):
    return JSONResponse({"message": "DOCMIND is running!"})


async def test_memory_endpoint(request: Request):
    thread_id = "test-thread"
    store.put(thread_id, "conversation", {"messages": [{"role": "user", "content": "Hello"}]})
    data = store.get(thread_id, "conversation")
    return JSONResponse({"thread_id": thread_id, "data": data})


routes = [
    Route("/ask", ask_endpoint, methods=["POST"]),
    Route("/health", health_endpoint),
    Route("/favicon.ico", favicon_endpoint),
    Route("/", root_endpoint),
    Route("/test-memory", test_memory_endpoint)
]

app = Starlette(routes=routes)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
