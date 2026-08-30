"""
Install pgvector extension in PostgreSQL database
Run this script to enable pgvector for vector similarity search
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine
from app.core.logging import setup_logging, get_logger

def install_pgvector():
    """Install pgvector extension"""
    setup_logging()
    logger = get_logger(__name__)
    
    try:
        with engine.connect() as conn:
            # Install pgvector extension
            logger.info("Installing pgvector extension...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            
            logger.info("SUCCESS: pgvector extension installed successfully!")
            
            # Verify installation
            result = conn.execute(text(
                "SELECT * FROM pg_extension WHERE extname = 'vector'"
            ))
            
            if result.fetchone():
                logger.info("pgvector extension is now active")
                return True
            else:
                logger.error("pgvector installation verification failed")
                return False
                
    except Exception as e:
        logger.error(f"Error installing pgvector: {e}")
        logger.error("You may need to install pgvector manually in PostgreSQL")
        logger.error("Visit: https://github.com/pgvector/pgvector#installation")
        return False

if __name__ == "__main__":
    if install_pgvector():
        sys.exit(0)
    else:
        sys.exit(1)