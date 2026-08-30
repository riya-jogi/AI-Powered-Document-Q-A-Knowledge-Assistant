# AI-Powered Document Q&A & Knowledge Assistant

A modular, locally deployable document intelligence platform implementing a complete **Retrieval-Augmented Generation (RAG)** pipeline. Upload documents, ask natural-language questions, and get grounded answers with source references.

## Features

- **Document Management** — Upload PDF, TXT, and DOCX files with validation
- **Document Processing** — Text extraction, cleaning, chunking with page tracking
- **Semantic Search** — Vector similarity search using Sentence Transformers + pgvector
- **RAG Q&A** — Local LLM answers via Ollama with source citations
- **Authentication** — JWT-based user registration and login
- **Conversation History** — Persist chat sessions linked to documents
- **React Frontend** — Dashboard, document upload, and chat interface
- **Docker Support** — One-command deployment with PostgreSQL and Ollama

## Architecture

```
User → React Frontend → FastAPI Backend
                              ├── Auth Service
                              ├── Document Service → PDF Parser → Text Chunker
                              ├── Embedding Service (Sentence Transformers)
                              ├── Retrieval Service (pgvector)
                              └── RAG Service → Ollama LLM
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL + pgvector |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| LLM | Ollama (local) |
| Frontend | React, Vite |
| Container | Docker Compose |

## Project Structure

```
├── app/
│   ├── api/           # REST API endpoints
│   ├── core/          # Config, database, security
│   ├── models/        # SQLAlchemy ORM models
│   ├── schemas/       # Pydantic request/response schemas
│   └── services/      # Business logic (RAG pipeline)
├── frontend/          # React web application
├── docker/            # Docker Compose and Dockerfiles
├── tests/             # Pytest test suite
├── scripts/           # Database setup utilities
└── docs/              # Documentation
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 16+ with [pgvector](https://github.com/pgvector/pgvector) extension
- [Ollama](https://ollama.ai/) with a model installed (e.g., `ollama pull qwen2:0.5b`)
- Node.js 18+ (for frontend)

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your database credentials

# Initialize database (ensure PostgreSQL is running)
python scripts/setup_env.py

# Start backend
python main.py
```

API docs available at: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: http://localhost:5173

### Docker Setup

```bash
cd docker
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Pull Ollama model: `docker exec -it docker-ollama-1 ollama pull qwen2:0.5b`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT token |
| POST | `/api/v1/documents` | Upload and process document |
| GET | `/api/v1/documents` | List user documents |
| DELETE | `/api/v1/documents/{id}` | Delete document |
| POST | `/api/v1/search` | Semantic search |
| POST | `/api/v1/qa/ask` | Ask a question (RAG) |
| POST | `/api/v1/conversations` | Create conversation |
| POST | `/api/v1/conversations/{id}/messages` | Send message in conversation |

## Environment Variables

See `.env.example` for all configuration options:

- `DATABASE_URL` — PostgreSQL connection string
- `SECRET_KEY` — JWT signing key
- `OLLAMA_BASE_URL` — Ollama API URL (default: http://localhost:11434)
- `OLLAMA_MODEL` — Model name (default:qwen2:7b)
- `EMBEDDING_MODEL` — Sentence Transformers model
- `CHUNK_SIZE` / `CHUNK_OVERLAP` — Text chunking parameters
- `TOP_K_RESULTS` — Number of chunks to retrieve

## Testing

```bash
pytest tests/ -v
```

## RAG Pipeline

1. **Indexing** (on upload): Extract text → Chunk → Generate embeddings → Store in pgvector
2. **Retrieval** (on question): Embed question → Cosine similarity search → Top-K chunks
3. **Generation**: Build context prompt → Send to Ollama → Return answer + sources

## Security

- JWT authentication on all document and Q&A endpoints
- User-scoped document access (User A cannot access User B's documents)
- File type and size validation
- Filename sanitization and path traversal prevention
- Grounded prompts to reduce hallucination

## Limitations

- Synchronous document processing (large PDFs may take time)
- CPU-based embeddings and LLM inference can be slow without GPU
- OCR not supported (scanned PDFs won't work)
- Single-document Q&A per query (no multi-document reasoning yet)

## Future Scope

- Background processing with Celery/Redis
- Hybrid search (keyword + semantic)
- OCR for scanned documents
- Multi-document reasoning
- Reranking for improved retrieval
- Evaluation dashboard with Recall@K metrics

## License

MIT
