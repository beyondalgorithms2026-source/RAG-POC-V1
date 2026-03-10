from sqlalchemy import text
from app.ingestion.ingest import ingest_documents
from app.core.logging import logger
from app.db.db import engine

def print_db_summary():
    print("\n--- DB VERIFICATION ---")
    with engine.connect() as conn:
        count_res = conn.execute(text("SELECT count(*) FROM documents;")).scalar()
        print(f"Total documents in DB: {count_res}")
        
        print("\nSample 5 rows:")
        rows = conn.execute(text("SELECT file_path, file_name, doc_type, contract_date, hash_sha256 FROM documents LIMIT 5;")).fetchall()
        for row in rows:
            print(f"  Path: {row[0]}")
            print(f"  Name: {row[1]}")
            print(f"  Type: {row[2]}")
            print(f"  Date: {row[3]}")
            print(f"  Hash: {row[4][:8]}...")
            print("  -")

if __name__ == "__main__":
    logger.info("Starting ingestion...")
    ingest_documents()
    logger.info("Ingestion complete.")
    print_db_summary()
