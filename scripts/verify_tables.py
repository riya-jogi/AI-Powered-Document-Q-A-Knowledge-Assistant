"""
Verify that database tables were created successfully
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.core.database import engine
from app.core.logging import setup_logging, get_logger

def verify_tables():
    """Verify database tables exist"""
    setup_logging()
    logger = get_logger(__name__)
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"Found {len(tables)} tables in database:")
        for table in tables:
            logger.info(f"  - {table}")
        
        expected_tables = ["documents", "document_chunks", "users"]
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if missing_tables:
            logger.error(f"Missing tables: {missing_tables}")
            return False
        else:
            logger.info("SUCCESS: All expected tables exist!")
            
            # Show table structures
            for table in expected_tables:
                logger.info(f"\nStructure of '{table}':")
                columns = inspector.get_columns(table)
                for column in columns:
                    logger.info(f"  {column['name']}: {column['type']}")
            
            return True
                
    except Exception as e:
        logger.error(f"Error verifying tables: {e}")
        return False

if __name__ == "__main__":
    if verify_tables():
        sys.exit(0)
    else:
        sys.exit(1)