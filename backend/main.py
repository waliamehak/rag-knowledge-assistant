from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request
from dotenv import load_dotenv
import os
import shutil
import uuid
from document_processor import extract_text_from_pdf, chunk_text
from openai_handler import generate_embedding
from pinecone_handler import store_chunks, create_index_if_not_exists
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

app = FastAPI(title="RAG Knowledge Assistant")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Create uploads folder and Pinecone index on startup
os.makedirs("uploads", exist_ok=True)
create_index_if_not_exists()

# Store job status in memory
jobs = {}


def process_document_task(job_id, file_path, filename):
    # Background task to process document
    try:
        jobs[job_id]["status"] = "processing"

        # Extract and chunk text
        text = extract_text_from_pdf(file_path)
        chunks = chunk_text(text)

        # Store in Pinecone
        chunk_count = store_chunks(chunks, filename)

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["chunks_created"] = chunk_count
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.get("/")
def read_root():
    return {"message": "RAG API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
):
    # Only accept PDFs
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Save file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Initialize job status
    jobs[job_id] = {"status": "queued", "filename": file.filename}

    # Start background processing
    background_tasks.add_task(process_document_task, job_id, file_path, file.filename)

    return {
        "job_id": job_id,
        "filename": file.filename,
        "message": "Document upload started",
    }


@app.get("/status/{job_id}")
def check_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.post("/query")
@limiter.limit("10/minute")
async def query_documents(request: Request, query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Search for similar chunks
    from pinecone_handler import search_similar_chunks
    from openai_handler import generate_answer

    context_chunks = search_similar_chunks(query, top_k=3)

    if not context_chunks:
        return {"query": query, "answer": "No relevant documents found.", "sources": []}

    # Generate answer using GPT-4
    answer = generate_answer(query, context_chunks)

    return {"query": query, "answer": answer, "sources": context_chunks}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
