# Database Setup Instructions

## Current Status
✅ Database connection: SUCCESSFUL  
❌ pgvector extension: NOT INSTALLED (requires system-level installation)

## Prerequisites
- PostgreSQL must be installed and running
- pgvector extension must be installed on the PostgreSQL system

## Step 1: Install pgvector Extension (System Level)

The pgvector extension must be installed on your PostgreSQL system before it can be enabled in your database.

### Windows Installation

#### Option 1: Chocolatey (if available)
```bash
choco install pgvector
```

#### Option 2: Manual Installation
Follow the official pgvector installation guide for Windows:
https://github.com/pgvector/pgvector#installation

This typically involves:
1. Downloading pgvector source
2. Compiling it with your PostgreSQL version
3. Copying the compiled files to your PostgreSQL extension directory

### Linux/Mac Installation
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-14-pgvector

# Mac with Homebrew
brew install pgvector
```

## Step 2: Enable pgvector in Database

After installing pgvector system-wide, run the installation script:
```bash
.venv\Scripts\activate
python scripts\install_pgvector.py
```

Or manually in PostgreSQL:
```sql
\c document_qa_db
CREATE EXTENSION vector;
```

## Step 2: Create Database and User

1. Open PostgreSQL command line or pgAdmin
2. Create a new database:
```sql
CREATE DATABASE document_qa_db;
```

3. Create a user (or use existing postgres user):
```sql
CREATE USER doc_qa_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE document_qa_db TO doc_qa_user;
```

4. Connect to the database and enable pgvector:
```sql
\c document_qa_db;
CREATE EXTENSION IF NOT EXISTS vector;
```

## Step 3: Configure Environment Variables

Edit the `.env` file in your project root with your actual database credentials:

```env
DATABASE_URL=postgresql://doc_qa_user:your_secure_password@localhost:5432/document_qa_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=document_qa_db
DB_USER=doc_qa_user
DB_PASSWORD=your_secure_password
```

## Step 4: Test Connection

Run the database connection test:
```bash
.venv\Scripts\activate
python scripts\test_db_connection.py
```

## Common Issues

### "password authentication failed"
- Check that the username and password in `.env` match your PostgreSQL setup
- Ensure the user has the correct privileges

### "connection refused"
- Ensure PostgreSQL is running
- Check that the port (default 5432) is correct
- Verify firewall settings

### "extension 'vector' does not exist"
- Install pgvector extension (see Step 1)
- Run the SQL command to enable it in your database

## Alternative: Use SQLite for Development

If you're having trouble with PostgreSQL, you can temporarily use SQLite for development:

1. Change the DATABASE_URL in `.env`:
```env
DATABASE_URL=sqlite:///./document_qa.db
```

2. Note: SQLite doesn't support pgvector, so you'll need to switch back to PostgreSQL for the vector search features later.