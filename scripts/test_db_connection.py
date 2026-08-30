"""
Test script to verify database connection and pgvector installation
Run this script to check if your PostgreSQL database is properly configured.
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import check_db_connection
from app.core.logging import setup_logging, get_logger

def main():
    """Test database connection"""
    setup_logging()
    logger = get_logger(__name__)
    
    logger.info("Testing database connection...")
    
    if check_db_connection():
        logger.info("SUCCESS: Database connection successful!")
        logger.info("Your PostgreSQL database is ready for use.")
        return 0
    else:
        logger.error("FAILED: Database connection failed!")
        logger.error("Please check your database configuration in .env file")
        logger.error("Make sure PostgreSQL is running and pgvector extension is installed")
        return 1

if __name__ == "__main__":
    sys.exit(main())