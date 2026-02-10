# RAG Knowledge Assistant

This project allows users to upload PDF files and ask natural language questions about their content. Answers are generated using GPT-4 and backed by semantic search over the uploaded documents.

## Features

- Upload PDF documents (stored in S3-direct uploads)
- Extract text and generate vector embeddings
- Ask questions in natural language
- Semantic search over document content  
- GPT-4 powered answers with citations  
- Asynchronous background processing  
- API rate limiting by IP (10 queries/min)
- Serverless deployment on AWS Lambda

## Tech Stack

**Backend:** Python, FastAPI, OpenAI GPT-4 API, OpenAI Embeddings API  Pinecone Vector Database, AWS Lambda, S3, IAM, API Gateway, Uvicorn, Pydantic  
**Frontend:** React, TypeScript, Axios, Vercel

## Live Demo

- **API:** https://e30fd4du98.execute-api.us-east-1.amazonaws.com/docs
- **Frontend:** https://rag-knowledge-assistant-virid.vercel.app


## System Workflow

1. User uploads a PDF document  
2. Backend extracts raw text  
3. Text is split into smaller chunks (2048-char segments with 200-char overlap) 
4. Embeddings are generated using OpenAI (OpenAI text-embedding-3-small)
5. Vectors are stored in Pinecone  
6. When a user asks a question:  
   - Relevant chunks are retrieved using semantic search  
   - Context is sent to GPT-4  
   - A final answer is generated with references  


## Local Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Environment Variables:**
```
OPENAI_API_KEY=your_key
PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=us-east-1
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload PDF file |
| GET | `/status/{job_id}` | Check upload status |
| POST | `/query` | Ask question |
| GET | `/health` | Health check |

## Architecture
```
User → React UI → FastAPI → Text Processing → OpenAI Embeddings → 
Pinecone Vector Store → Semantic Search → GPT-4 → Answer
```

## Work to be done

### Must have 
- S3 pre-signed URLs for direct upload (bypass 6MB API Gateway limit)
- Async embedding processing with background workers
- Batch PDF upload support
- Query result caching (Redis/DynamoDB)

### Nice to have
- Improved RAG quality (opmtimize chunkinig & overlap)
- Streaming GPT-4 responses
- Support for TXT, DOCX, CSV file types
- Per-user rate limiting (more than just IP)
- Error logging (Sentry/CloudWatch) & dashboards