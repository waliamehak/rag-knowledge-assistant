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

**Backend:** Python, FastAPI, OpenAI GPT-4 API, OpenAI Embeddings API, Pinecone Vector Database, AWS Lambda, S3, SQS, RDS PostgreSQL, Redis (Upstash), SlowAPI, IAM, API Gateway, Uvicorn, Pydantic
**Frontend:** React, TypeScript, Axios, Vercel

## Live Demo

- **API:** https://e30fd4du98.execute-api.us-east-1.amazonaws.com/docs
- **Frontend:** https://rag-knowledge-assistant-virid.vercel.app


## System Workflow

1. User selects PDFs — frontend calls `/presign-batch` to get S3 upload URLs
2. Files uploaded directly to S3 using pre-signed URLs (bypasses API Gateway 6MB limit)
3. `/confirm` called per file — job queued in SQS
4. Lambda worker picks up SQS message, downloads from S3, extracts text, splits into context-aware chunks (up to 1000 chars, 200-char overlap), embeds in batch, stores vectors in Pinecone — updates job status in RDS throughout
5. When a user asks a question:
   - Redis cache checked first
   - Relevant chunks retrieved via semantic search (top-5)
   - Context sent to GPT-4
   - Answer returned with source filename and chunk index


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
DB_HOST=your_rds_host
DB_PORT=5432
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
SQS_QUEUE_URL=your_queue_url
REDIS_URL=your_upstash_url
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
| POST | `/presign` | Get presigned S3 URL for single file |
| POST | `/presign-batch` | Get presigned S3 URLs for multiple files |
| POST | `/confirm` | Confirm upload and trigger processing |
| POST | `/upload` | Legacy direct upload (single file) |
| GET | `/status/{job_id}` | Check job status |
| POST | `/query` | Ask question, returns answer + sources |
| GET | `/health` | Health check |

## Architecture
```
User → React UI → FastAPI → S3 (direct upload) → SQS → Lambda Worker → Text Processing → OpenAI Embeddings →
Pinecone Vector Store → Semantic Search → GPT-4 → Answer
```

## Work to be done

### Must have
- S3 pre-signed URLs for direct upload (bypass 6MB API Gateway limit) (done)
- Async embedding processing with background workers (done)
- Batch PDF upload support (done)
- Query result caching (Redis/DynamoDB) (done)

### Nice to have
- Improve RAG quality (optimize chunking & overlap)
- Streaming GPT-4 responses
- Support for TXT, DOCX, CSV file types
- Per-user rate limiting (more than just IP)
- Error logging (Sentry/CloudWatch) & dashboards