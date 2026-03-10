import time
from app.core.logging import logger
from app.core.config import settings
from app.db.repo_embeddings import get_chunks_to_embed, update_chunk_embeddings
from app.embedding.embedder import embed_texts, get_expected_dim

def process_embeddings(force: bool = False, limit: int = None, doc_id: int = None):
    start_time = time.time()
    
    logger.info("Fetching chunks to embed...")
    chunks = get_chunks_to_embed(force=force, limit=limit, doc_id=doc_id)
    
    stats = {
        "chunks_total_selected": len(chunks),
        "chunks_embedded": 0,
        "chunks_skipped": 0,
        "chunks_failed": 0,
        "time_taken": 0.0
    }
    
    if not chunks:
        logger.info("No chunks found requiring embeddings.")
        return stats
        
    logger.info(f"Selected {len(chunks)} chunks. Preparing to embed...")
    
    # Pre-flight the model to get the expected dimensions early
    expected_dim = get_expected_dim()
    batch_size = settings.EMBEDDING_BATCH_SIZE
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} chunks)...")
        
        valid_texts = []
        valid_ids = []
        
        # Validation Pass
        for chunk in batch:
            text = chunk["chunk_text"].strip()
            if not text:
                logger.warning(f"Chunk ID {chunk['id']} has empty text. Skipping.")
                stats["chunks_failed"] += 1
                continue
                
            valid_texts.append(text)
            valid_ids.append(chunk["id"])
            
        if not valid_texts:
            continue
            
        try:
            # Embed Passage
            embeddings = embed_texts(valid_texts)
            
            # Dimension Safety Check Before Database Operation
            db_updates = []
            for chunk_id, embedding_vector in zip(valid_ids, embeddings):
                if len(embedding_vector) != expected_dim:
                    logger.error(f"Dimension mismatch! Expected {expected_dim}, got {len(embedding_vector)} for chunk_id {chunk_id}")
                    stats["chunks_failed"] += 1
                    continue
                    
                db_updates.append((chunk_id, embedding_vector))
                
            # Database Transaction
            if db_updates:
                update_chunk_embeddings(db_updates)
                stats["chunks_embedded"] += len(db_updates)
                
        except Exception as e:
            logger.error(f"Batch failed during embedding generation or database updating: {str(e)}")
            stats["chunks_failed"] += len(valid_texts)
            
    stats["time_taken"] = round(time.time() - start_time, 2)
    
    # Output metrics
    print("\n" + "="*40)
    print("EMBEDDING SUMMARY")
    print("="*40)
    print(f"Chunks Selected: {stats['chunks_total_selected']}")
    print(f"Chunks Embedded: {stats['chunks_embedded']}")
    print(f"Chunks Skipped:  {stats['chunks_skipped']}")
    print(f"Chunks Failed:   {stats['chunks_failed']}")
    print(f"Time Taken:      {stats['time_taken']} seconds")
    print("="*40)
    
    return stats
