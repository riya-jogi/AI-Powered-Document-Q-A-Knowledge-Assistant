-- Database initialization script for PostgreSQL with pgvector extension
-- Run this script to create the database and enable pgvector extension

-- Create database if it doesn't exist
-- Note: This needs to be run as a superuser or with appropriate privileges
-- CREATE DATABASE document_qa_db;

-- Connect to the database
\c document_qa_db;

-- Enable pgvector extension
-- This extension is required for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify pgvector is installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Create a test table to verify pgvector works
-- This will be removed when we use SQLAlchemy models
CREATE TABLE IF NOT EXISTS vector_test (
    id SERIAL PRIMARY KEY,
    embedding vector(384)
);

-- Insert a test vector
INSERT INTO vector_test (embedding) VALUES ('[0.1,0.2,0.3,0.4]');

-- Test vector similarity
SELECT * FROM vector_test ORDER BY embedding <-> '[0.1,0.2,0.3,0.4]' LIMIT 1;

-- Clean up test table
DROP TABLE IF EXISTS vector_test;

-- Grant privileges (adjust username as needed)
-- GRANT ALL PRIVILEGES ON DATABASE document_qa_db TO your_db_user;
-- GRANT ALL PRIVILEGES ON SCHEMA public TO your_db_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_db_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_db_user;