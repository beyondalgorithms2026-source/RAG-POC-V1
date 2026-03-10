import argparse
from app.chunking.process import process_chunks
from app.core.logging import logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process extracted documents into text chunks.")
    parser.add_argument("--force", action="store_true", help="Force re-chunking of all documents, even if unchanged.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of documents to process.")
    
    args = parser.parse_args()
    
    logger.info(f"Starting chunking pipeline (force={args.force}, limit={args.limit})...")
    process_chunks(force=args.force, limit=args.limit)
    logger.info("Chunking pipeline complete.")
