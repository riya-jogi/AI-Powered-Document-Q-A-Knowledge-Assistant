"""
Setup script to help configure environment variables
Run this script to create your .env file with your database credentials
"""

import os
import sys

def setup_env_file():
    """Create .env file with user's database credentials"""
    
    print("=== Database Configuration Setup ===")
    print("Please enter your PostgreSQL database credentials:")
    print()
    
    db_host = input("Database host (default: localhost): ") or "localhost"
    db_port = input("Database port (default: 5432): ") or "5432"
    db_name = input("Database name (default: document_qa_db): ") or "document_qa_db"
    db_user = input("Database username (default: postgres): ") or "postgres"
    db_password = input("Database password: ")
    
    if not db_password:
        print("ERROR: Database password is required")
        return False
    
    env_content = f"""# Database Configuration
DATABASE_URL=postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}
DB_HOST={db_host}
DB_PORT={db_port}
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2:7b

# File Upload Configuration
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads
ALLOWED_FILE_TYPES=pdf,docx,txt

# Embedding Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5

# Logging
LOG_LEVEL=INFO
"""
    
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"SUCCESS: .env file created at {env_path}")
        print("Please run the database connection test again")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create .env file: {e}")
        return False

if __name__ == "__main__":
    if setup_env_file():
        sys.exit(0)
    else:
        sys.exit(1)