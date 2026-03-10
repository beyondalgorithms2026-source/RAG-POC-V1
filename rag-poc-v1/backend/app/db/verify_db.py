import sys
from sqlalchemy import text
from app.db.db import engine
from app.core.logging import logger

def verify_db():
    checks = {
        "pgvector extension exists": False,
        "documents table exists": False,
        "chunks table exists": False,
        "chunks.embedding is vector(384)": False,
        "vector index exists on chunks.embedding": False
    }

    try:
        with engine.connect() as conn:
            # 1. Check pgvector extension
            res = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';")).first()
            if res:
                checks["pgvector extension exists"] = True

            # 2. Check documents table
            res = conn.execute(text("SELECT tablename FROM pg_tables WHERE tablename = 'documents';")).first()
            if res:
                checks["documents table exists"] = True

            # 3. Check chunks table
            res = conn.execute(text("SELECT tablename FROM pg_tables WHERE tablename = 'chunks';")).first()
            if res:
                checks["chunks table exists"] = True

            # 4. Check chunks.embedding type
            res = conn.execute(text("""
                SELECT data_type, udt_name 
                FROM information_schema.columns 
                WHERE table_name = 'chunks' AND column_name = 'embedding';
            """)).first()
            
            # Additional check to verify dimension = 384
            # For pgvector, the modifier is the dimension. We check the format_type from pg_attribute
            res_dim = conn.execute(text("""
                SELECT format_type(a.atttypid, a.atttypmod)
                FROM pg_attribute a
                JOIN pg_class c ON a.attrelid = c.oid
                WHERE c.relname = 'chunks' AND a.attname = 'embedding';
            """)).first()

            if res_dim and res_dim[0] == 'vector(384)':
                checks["chunks.embedding is vector(384)"] = True

            # 5. Check if vector index exists
            res = conn.execute(text("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'chunks' AND (indexname = 'chunks_embedding_hnsw' OR indexname = 'chunks_embedding_ivfflat');
            """)).first()
            if res:
                checks["vector index exists on chunks.embedding"] = True

    except Exception as e:
        logger.error(f"Error connecting or executing queries: {e}")

    all_passed = True
    print("\n--- DB VERIFICATION RESULTS ---")
    for check_name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {check_name}")
        if not passed:
            all_passed = False
            
    if not all_passed:
        print("\nVerification FAIL. Some checks did not pass.")
        sys.exit(1)
    else:
        print("\nVerification SUCCESS. All checks passed.")
        sys.exit(0)

if __name__ == "__main__":
    verify_db()
