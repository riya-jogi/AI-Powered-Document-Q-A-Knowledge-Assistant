"""
Check if pgvector extension is installed in PostgreSQL
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine
from app.core.logging import setup_logging, get_logger

def check_pgvector():
    """Check if pgvector extension is installed"""
    setup_logging()
    logger = get_logger(__name__)
    
    try:
        with engine.connect() as conn:
            # Check if pgvector extension exists
            result = conn.execute(text(
                "SELECT * FROM pg_extension WHERE extname = 'vector'"
            ))
            
            if result.fetchone():
                logger.info("SUCCESS: pgvector extension is installed!")
                
                # Get pgvector version
                version_result = conn.execute(text(
                    "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
                ))
                version = version_result.fetchone()
                if version:
                    logger.info(f"pgvector version: {version[0]}")
                
                return True
            else:
                logger.error("FAILED: pgvector extension is NOT installed!")
                logger.error("Please install pgvector extension in PostgreSQL")
                logger.error("Run: CREATE EXTENSION vector;")
                return False
                
    except Exception as e:
        logger.error(f"Error checking pgvector: {e}")
        return False

if __name__ == "__main__":
    if check_pgvector():
        sys.exit(0)
    else:
        sys.exit(1)