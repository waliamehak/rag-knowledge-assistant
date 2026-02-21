from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os
import shutil
import uuid
from document_processor import extract_text_from_pdf, chunk_text
from pinecone_handler import store_chunks, create_index_if_not_exists
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from s3_handler import upload_to_s3, generate_presigned_url
from fastapi.middleware.cors import CORSMiddleware
from redis_handler import get_cached_query, cache_query_result
from db_handler import create_jobs_table, create_job, update_job, get_job
from sqs_handler import enqueue_document

load_dotenv()

app = FastAPI(title="RAG Knowledge Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Create uploads folder and Pinecone index on startup
os.makedirs("/tmp/uploads", exist_ok=True)
create_index_if_not_exists()
create_jobs_table()


def process_document_task(job_id, file_path, filename):
    # Background task to process document
    try:
        update_job(job_id, status="processing")

        # Upload to S3
        s3_key = f"documents/{filename}"
        upload_to_s3(file_path, s3_key)

        # Extract and chunk text
        text = extract_text_from_pdf(file_path)
        chunks = chunk_text(text)

        # Store in Pinecone
        chunk_count = store_chunks(chunks, filename)

        # Clean up local file
        os.remove(file_path)

        update_job(job_id, status="completed", chunks_created=chunk_count, s3_key=s3_key)
    except Exception as e:
        update_job(job_id, status="failed", error=str(e))



@app.get("/")
def read_root():
    return {"message": "RAG API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/presign")
async def get_presigned_url(filename: str):
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")

    job_id = str(uuid.uuid4())
    s3_key = f"documents/{filename}"

    # Generate a temporary S3 URL — client uploads directly, bypassing the 6MB API Gateway limit
    upload_url = generate_presigned_url(s3_key)

    create_job(job_id, filename, status="pending")

    return {"job_id": job_id, "upload_url": upload_url, "s3_key": s3_key}


class BatchPresignRequest(BaseModel):
    filenames: List[str]


@app.post("/presign-batch")
async def get_presigned_urls_batch(request: BatchPresignRequest):
    # Generate a presigned URL and job entry for each file in one shot
    results = []
    for filename in request.filenames:
        if not filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"{filename} is not a PDF")
        job_id = str(uuid.uuid4())
        s3_key = f"documents/{filename}"
        upload_url = generate_presigned_url(s3_key)
        create_job(job_id, filename, status="pending")
        results.append({"job_id": job_id, "upload_url": upload_url, "s3_key": s3_key})
    return results


@app.post("/confirm")
async def confirm_upload(job_id: str, s3_key: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_job(job_id, status="queued")
    enqueue_document(job_id, s3_key, job["filename"])

    return {"job_id": job_id, "status": "queued"}


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
    file_path = f"/tmp/uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    create_job(job_id, file.filename, status="queued")
    background_tasks.add_task(process_document_task, job_id, file_path, file.filename)

    return {
        "job_id": job_id,
        "filename": file.filename,
        "message": "Document upload started",
    }


@app.get("/status/{job_id}")
def check_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/query")
@limiter.limit("10/minute")
async def query_documents(request: Request, query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Check Redis cache first
    cached_result = get_cached_query(query)
    if cached_result:
        return cached_result

    # Search for similar chunks
    from pinecone_handler import search_similar_chunks
    from openai_handler import generate_answer

    context_chunks = search_similar_chunks(query, top_k=5)

    if not context_chunks:
        result = {
            "query": query,
            "answer": "No relevant documents found.",
            "sources": [],
        }
        cache_query_result(query, result)
        return result

    # Generate answer using GPT-4
    answer = generate_answer(query, [c["text"] for c in context_chunks])

    result = {"query": query, "answer": answer, "sources": context_chunks}

    # Cache the result
    cache_query_result(query, result)

    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
