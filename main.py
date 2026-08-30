from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.database import init_db, check_db_connection
from app.models import Document, DocumentChunk, User, Conversation, Message, RetrievalLog
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.api.qa import router as qa_router
from app.api.conversations import router as conversations_router
from app.api.upload import router as upload_router
from app.services.llm_service import llm_service

load_dotenv()

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting application initialization...")

    if check_db_connection():
        logger.info("Database connection verified")
        init_db()
    else:
        logger.warning("Database connection failed - some features may not work")

    ollama_ok = await llm_service.check_availability()
    if ollama_ok:
        logger.info("Ollama LLM service is available")
    else:
        logger.warning(
            "Ollama is not reachable - Q&A will fail until Ollama is running "
            f"at {settings.OLLAMA_BASE_URL}"
        )

    yield

    logger.info("Shutting down application...")


app = FastAPI(
    title="AI-Powered Document Q&A & Knowledge Assistant",
    description="A RAG-based document Q&A system using local AI models",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(qa_router)
app.include_router(conversations_router)
app.include_router(upload_router)


@app.get("/")
async def root():
    """Root endpoint to verify the API is running."""
    return {
        "message": "AI-Powered Document Q&A & Knowledge Assistant API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    db_status = "connected" if check_db_connection() else "disconnected"
    ollama_status = "available" if await llm_service.check_availability() else "unavailable"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "document-qa-assistant",
        "database": db_status,
        "ollama": ollama_status,
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
