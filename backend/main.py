from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
import os
import shutil
from document_processor import extract_text_from_pdf, chunk_text
from openai_handler import generate_embedding
from pinecone_handler import store_chunks, create_index_if_not_exists

load_dotenv()

app = FastAPI(title="RAG Knowledge Assistant")

# Create uploads folder and Pinecone index on startup
os.makedirs("uploads", exist_ok=True)
create_index_if_not_exists()


@app.get("/")
def read_root():
    return {"message": "RAG API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Only accept PDFs
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")

    # Save file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract and chunk text
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)

    # Generate embeddings and store in Pinecone
    chunk_count = store_chunks(chunks, file.filename)

    return {
        "filename": file.filename,
        "chunks_created": chunk_count,
        "message": "Document uploaded and indexed successfully",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
