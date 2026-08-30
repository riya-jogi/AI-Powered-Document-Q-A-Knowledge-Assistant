"""
Database connection management using SQLAlchemy
"""

from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _is_sqlite_url(database_url: str) -> bool:
    """Return True when the project is configured to use SQLite."""
    return database_url.startswith("sqlite")


# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if _is_sqlite_url(settings.DATABASE_URL) else {},
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Used in FastAPI endpoint dependencies.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating pgvector extension and all tables.
    Call this during application startup.
    """
    try:
        if _is_sqlite_url(settings.DATABASE_URL):
            Base.metadata.create_all(bind=engine)
            logger.info("SQLite database initialized successfully")
            return

        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        Base.metadata.create_all(bind=engine)
        _create_vector_index()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

    # Backfill missing columns for older database instances created before schema changes.
    _ensure_document_user_id_column()
    _ensure_document_chunk_columns()


def _create_vector_index():
    """Create HNSW index on embeddings for faster similarity search."""
    if _is_sqlite_url(settings.DATABASE_URL):
        return

    try:
        with engine.connect() as conn:
            conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding
                    ON document_chunks
                    USING hnsw (embedding vector_cosine_ops)
                    """
                )
            )
            conn.commit()
            logger.info("Vector index created or already exists")
    except Exception as e:
        logger.warning(f"Could not create vector index (may need data first): {e}")


def _ensure_document_user_id_column():
    """Repair older database schemas created before the `documents.user_id` column existed."""
    if _is_sqlite_url(settings.DATABASE_URL):
        return

    with engine.begin() as conn:
        has_column = conn.execute(
            text(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'documents'
                  AND column_name = 'user_id'
                """
            )
        ).fetchone()

        if has_column is None:
            conn.execute(text("ALTER TABLE documents ADD COLUMN user_id INTEGER"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents (user_id)"))
            conn.execute(
                text(
                    """
                    UPDATE documents
                    SET user_id = (SELECT MIN(id) FROM users)
                    WHERE user_id IS NULL
                      AND EXISTS (SELECT 1 FROM users)
                    """
                )
            )
            logger.warning(
                "Applied database migration: added missing documents.user_id column and index"
            )


def _ensure_document_chunk_columns():
    """Repair older database schemas that predate the chunk metadata columns."""
    if _is_sqlite_url(settings.DATABASE_URL):
        return

    required_columns = {
        "chunk_index": "INTEGER NOT NULL DEFAULT 0",
        "content": "TEXT NOT NULL DEFAULT ''",
        "page_number": "INTEGER",
        "token_count": "INTEGER DEFAULT 0",
        "chunk_type": "VARCHAR(50) DEFAULT 'text'",
        "chunk_metadata": "TEXT",
        "embedding": "vector(384)",
    }

    with engine.begin() as conn:
        existing_columns = conn.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'document_chunks'
                """
            )
        ).fetchall()

        existing_names = {row[0] for row in existing_columns}
        missing = [name for name in required_columns if name not in existing_names]

        for column_name in missing:
            sql = f"ALTER TABLE document_chunks ADD COLUMN {column_name} {required_columns[column_name]}"
            conn.execute(text(sql))
            logger.warning(
                f"Applied database migration: added missing document_chunks.{column_name} column"
            )

        if "embedding" in missing:
            conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding
                    ON document_chunks
                    USING hnsw (embedding vector_cosine_ops)
                    """
                )
            )


def check_db_connection():
    """
    Check if database connection is working.
    Returns True if connection is successful, False otherwise.
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection check successful")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False