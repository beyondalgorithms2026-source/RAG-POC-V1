import os
from app.core.logging import logger
from app.core.config import settings
from app.db.repo_documents import get_all_documents, update_document_chunked_hash
from app.db.repo_chunks import delete_chunks_for_document, insert_chunks
from app.chunking.splitter import split_text

def process_chunks(force: bool = False, limit: int = None):
    extract_dir = os.path.abspath(settings.EXTRACT_DIR)
    
    docs = get_all_documents()
    logger.info(f"Found {len(docs)} documents in the database.")
    
    if limit is not None:
        docs = docs[:limit]
        logger.info(f"Limiting processing to {limit} documents.")
        
    stats = {
        "docs_total": len(docs),
        "docs_chunked": 0,
        "docs_skipped": 0,
        "docs_failed": 0,
        "total_chunks_created": 0
    }
    
    first_few_chunked = []
    
    for doc in docs:
        doc_id = doc.id
        file_name = doc.file_name
        current_hash = doc.hash_sha256
        chunked_hash = doc.chunked_hash_sha256
        
        try:
            # Idempotency check
            if not force and current_hash == chunked_hash:
                logger.info(f"SKIPPED chunking for {file_name}: hashes match (unchanged).")
                stats["docs_skipped"] += 1
                continue
                
            # Read extracted text
            text_filename = f"{current_hash}__{file_name}.txt"
            text_path = os.path.join(extract_dir, text_filename)
            
            if not os.path.exists(text_path):
                logger.warning(f"FAILED: Extracted text not found for {file_name} at {text_path}")
                stats["docs_failed"] += 1
                continue
                
            with open(text_path, "r", encoding="utf-8") as f:
                text = f.read()
                
            if not text.strip():
                logger.warning(f"FAILED: Empty text file for {file_name}")
                stats["docs_failed"] += 1
                continue
                
            # Split text into chunks
            chunks = split_text(text)
            
            # Delete old chunks and insert new ones
            delete_chunks_for_document(doc_id)
            if chunks:
                insert_chunks(doc_id, chunks)
                
            # Mark document as chunked with the current hash
            update_document_chunked_hash(doc_id, current_hash)
                
            stats["docs_chunked"] += 1
            stats["total_chunks_created"] += len(chunks)
            logger.info(f"PROCESSED: {file_name} -> {len(chunks)} chunks")
            
            if len(first_few_chunked) < 3:
                first_few_chunked.append((file_name, len(chunks)))
                
        except Exception as e:
            logger.error(f"FAILED processing {file_name}: {str(e)}")
            stats["docs_failed"] += 1
            
    # Output final summary table
    print("\n" + "="*40)
    print("CHUNKING SUMMARY")
    print("="*40)
    print(f"docs_total:           {stats['docs_total']}")
    print(f"docs_chunked:         {stats['docs_chunked']}")
    print(f"docs_skipped:         {stats['docs_skipped']}")
    print(f"docs_failed:          {stats['docs_failed']}")
    print(f"total_chunks_created: {stats['total_chunks_created']}")
    print("="*40)
    
    if first_few_chunked:
        print("First Processed Files:")
        for fname, ccount in first_few_chunked:
            print(f"  - {fname}: {ccount} chunks")
            
    return stats
