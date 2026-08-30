# RAG Pipeline Documentation

## Overview

Retrieval-Augmented Generation (RAG) combines document retrieval with LLM generation to produce grounded answers.

## Stage A — Indexing (on document upload)

1. **Text Extraction** — PyMuPDF extracts text page-by-page from PDFs
2. **Text Cleaning** — Remove artifacts while preserving structure
3. **Chunking** — Split into ~1000 character chunks with 200 char overlap
4. **Embedding** — Generate 384-dimensional vectors using all-MiniLM-L6-v2
5. **Storage** — Store chunks and embeddings in PostgreSQL with pgvector

## Stage B — Question Answering (per query)

1. **Query Embedding** — Convert question to vector using same model
2. **Similarity Search** — Find top-K chunks by cosine distance
3. **Context Building** — Format retrieved chunks with page references
4. **LLM Generation** — Send grounded prompt to Ollama
5. **Response** — Return answer with source citations

## Prompt Design

The system prompt instructs the LLM to:
- Answer ONLY from provided context
- Refuse when information is not available
- Treat document content as untrusted data
- Not follow instructions embedded in documents

## Hallucination Mitigation

- Retrieval-first architecture (LLM never sees full document)
- Explicit refusal instructions in system prompt
- Source citations for verification
- Similarity threshold filtering

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| CHUNK_SIZE | 1000 | Characters per chunk |
| CHUNK_OVERLAP | 200 | Overlap between chunks |
| TOP_K_RESULTS | 5 | Chunks retrieved per query |
| EMBEDDING_MODEL | all-MiniLM-L6-v2 | Sentence Transformers model |
| OLLAMA_MODEL | qwen2:7b | Local LLM model |

## Evaluation

Use the search endpoint (`POST /api/v1/search`) to test retrieval independently from LLM generation. Measure Recall@K by checking if expected chunks appear in top results.
