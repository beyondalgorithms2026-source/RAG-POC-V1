import os
from sqlalchemy import text
from app.db.db import engine
from app.core.logging import logger

def run_migrations():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if not os.path.exists(schema_path):
        logger.error(f"Schema file not found at {schema_path}")
        return

    with open(schema_path, "r") as f:
        sql = f.read()

    logger.info("Running base schema migrations...")
    with engine.begin() as conn:
        conn.execute(text(sql))
    logger.info("Base schema created successfully.")

    logger.info("Applying patch migrations...")
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS chunked_hash_sha256 TEXT;"))
        
        # M10 Hybrid Retrieval Patch
        conn.execute(text("ALTER TABLE chunks ADD COLUMN IF NOT EXISTS search_tsv tsvector;"))
        conn.execute(text("UPDATE chunks SET search_tsv = to_tsvector('english', chunk_text) WHERE search_tsv IS NULL;"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS chunks_search_tsv_gin ON chunks USING gin(search_tsv);"))
    logger.info("Patch migrations completed.")

    with engine.begin() as conn:
        logger.info("Creating standard indexes...")
        conn.execute(text("CREATE INDEX IF NOT EXISTS chunks_docid_idx ON chunks(document_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS documents_doc_type_idx ON documents(doc_type);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS documents_contract_date_idx ON documents(contract_date);"))

        logger.info("Attempting to create HNSW vector index...")
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw ON chunks USING hnsw (embedding vector_cosine_ops);"))
            logger.info("HNSW index created successfully.")
        except Exception as e:
            logger.warning(f"Failed to create HNSW index: {e}")
            logger.warning("Falling back to IVFFLAT index...")
            try:
                # Need to use a new transaction/savepoint ideally since the above failed, 
                # but in SQLAlchemy's begin() catching exceptions leaves the transaction aborted.
                # So we catch the error, then we will reconnect in another begin block.
                pass
            except Exception:
                pass

    # If the above transaction failed for HNSW, we need a new transaction for IVFFLAT
    # Check if HNSW was created
    hnsw_created = False
    with engine.connect() as conn:
        result = conn.execute(text("SELECT indexname FROM pg_indexes WHERE tablename = 'chunks' AND indexname = 'chunks_embedding_hnsw';"))
        if result.first():
            hnsw_created = True

    if not hnsw_created:
        try:
            with engine.begin() as conn:
                logger.info("Creating IVFFLAT index as fallback...")
                conn.execute(text("CREATE INDEX IF NOT EXISTS chunks_embedding_ivfflat ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);"))
                logger.info("IVFFLAT index created successfully.")
        except Exception as e:
            logger.error(f"Failed to create IVFFLAT index: {e}")

    logger.info("Migrations completed successfully.")

if __name__ == "__main__":
    run_migrations()
