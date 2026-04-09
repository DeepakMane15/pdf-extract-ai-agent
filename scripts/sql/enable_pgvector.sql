-- Run manually against any database that has pgvector available on the server, e.g.:
--   psql "$DATABASE_URL" -f scripts/sql/enable_pgvector.sql
--   docker exec -i <container> psql -U postgres -d mydb -f - < scripts/sql/enable_pgvector.sql
CREATE EXTENSION IF NOT EXISTS vector;
