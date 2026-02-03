# RAG Knowledge Assistant

AI-powered document Q&A system using Retrieval-Augmented Generation.

## Features

- Upload PDF documents
- Ask questions in natural language
- Get GPT-4 answers with source citations
- Async background processing
- Rate limiting (10 queries/min)
- Serverless deployment

## Tech Stack

**Backend:** Python, FastAPI, OpenAI GPT-4, Pinecone, AWS Lambda, S3, API Gateway  
**Frontend:** React, TypeScript, Vercel

## Live Demo

- **API:** https://e30fd4du98.execute-api.us-east-1.amazonaws.com/docs
- **Frontend:** https://rag-knowledge-assistant-virid.vercel.app


## System Workflow

1. User uploads PDF → FastAPI backend
2. Extract text → chunk into 2048-char segments (200-char overlap)
3. Generate embeddings (OpenAI text-embedding-3-small)
4. Store vectors in Pinecone
5. Query → semantic search → GPT-4 generates answer with sources

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
