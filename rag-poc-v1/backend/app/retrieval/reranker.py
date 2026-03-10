from sentence_transformers import CrossEncoder
from app.core.config import settings
from app.core.logging import logger
from typing import List, Dict

RERANK_CHUNK_CAP = 2000

_reranker = None

def get_reranker():
    global _reranker
    if _reranker is None:
        logger.info(f"Loading reranker model: {settings.RERANK_MODEL}")
        _reranker = CrossEncoder(settings.RERANK_MODEL)
        logger.info("Reranker model loaded successfully.")
    return _reranker

def rerank(question: str, chunks: List[Dict], top_k: int) -> List[Dict]:
    """Score each chunk against the question using a cross-encoder and return re-sorted top_k."""
    model = get_reranker()
    
    # Build (question, passage) pairs using full chunk_text capped at 2000 chars
    pairs = [(question, c["snippet"][:RERANK_CHUNK_CAP]) for c in chunks]
    
    scores = model.predict(pairs)
    
    for i, c in enumerate(chunks):
        c["rerank_score"] = float(scores[i])
        
    chunks.sort(key=lambda x: x["rerank_score"], reverse=True)
    
    return chunks[:top_k]
