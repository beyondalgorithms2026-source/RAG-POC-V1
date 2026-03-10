# Backend

## Environment Variables
- `DATABASE_URL`: Connection string for Postgres (see `.env.example`).

## Validating the Setup
- Verify pgvector extension exists by connecting to the DB and running `\dx`.
- Verify tables exist with `\dt`.
- Check indexes using `\d chunks`.
- *Note: We use HNSW for vector indexing because it's supported by pgvector >= 0.5.0 on arm64 and avoids recalling phase. If your environment does not support HNSW, you may fall back to IVFFLAT.*
