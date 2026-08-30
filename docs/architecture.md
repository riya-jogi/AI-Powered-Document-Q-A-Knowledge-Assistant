# Architecture

## System Overview

The AI-Powered Document Q&A & Knowledge Assistant is a modular monolith built with FastAPI. It implements a complete RAG pipeline for document-grounded question answering.

## Components

### Backend Services

| Service | Responsibility |
|---------|---------------|
| Auth Service | User registration, JWT login, access control |
| Document Service | File upload, validation, storage |
| Document Processor | PDF/TXT/DOCX text extraction and chunking |
| Embedding Service | Sentence Transformers model for vector generation |
| Retrieval Service | pgvector cosine similarity search |
| RAG Service | Context building and LLM orchestration |
| LLM Service | Ollama API integration |

### Data Flow — Indexing

```
Upload → Validate → Store File → Extract Text → Clean → Chunk → Embed → pgvector
```

### Data Flow — Question Answering

```
Question → Embed → Vector Search → Top-K Chunks → Context Builder → Ollama → Answer + Sources
```

## Database Schema

- **users** — Authentication and ownership
- **documents** — Uploaded file metadata
- **document_chunks** — Text chunks with 384-dim embeddings
- **conversations** — Chat sessions linked to documents
- **messages** — User and assistant messages
- **retrieval_logs** — Retrieved chunks per answer (for evaluation)

## Technology Choices

- **PostgreSQL + pgvector** — Single database for relational data and vector search
- **Sentence Transformers** — Local, free embeddings without API keys
- **Ollama** — Local LLM inference without cloud dependencies
- **FastAPI** — Async REST API with automatic OpenAPI documentation
