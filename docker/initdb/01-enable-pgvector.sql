-- Runs automatically on first container start (empty data volume only).
-- Requires a Postgres image with pgvector installed (e.g. pgvector/pgvector).
CREATE EXTENSION IF NOT EXISTS vector;
