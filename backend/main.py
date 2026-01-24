from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
import os
import shutil
from document_processor import extract_text_from_pdf, chunk_text

load_dotenv()

app = FastAPI(title="RAG Knowledge Assistant")

# Create uploads folder if it doesn't exist
os.makedirs("uploads", exist_ok=True)


@app.get("/")
def read_root():
    return {"message": "RAG API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Only accept PDFs for now
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")

    # Save file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract and chunk text
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)

    return {
        "filename": file.filename,
        "chunks_created": len(chunks),
        "message": "Document uploaded and processed",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
