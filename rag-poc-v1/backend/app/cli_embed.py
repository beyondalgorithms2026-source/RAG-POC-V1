import argparse
from app.embedding.process import process_embeddings
from app.core.logging import logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate embeddings for text chunks and store them in PostgreSQL.")
    parser.add_argument("--force", action="store_true", help="Force re-generation of embeddings even if they exist.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of chunks to embed.")
    parser.add_argument("--doc-id", type=int, default=None, help="Process chunks strictly for this document ID only.")
    
    args = parser.parse_args()
    
    logger.info(f"Starting embeddings pipeline (force={args.force}, limit={args.limit}, doc_id={args.doc_id})...")
    process_embeddings(force=args.force, limit=args.limit, doc_id=args.doc_id)
    logger.info("Embeddings pipeline complete.")
