from sqlalchemy import text
from app.db.db import engine
from typing import List, Dict, Optional
import math

def get_chunks_to_embed(force: bool = False, limit: Optional[int] = None, doc_id: Optional[int] = None) -> List[Dict]:
    conditions = []
    params = {}
    
    if not force:
        conditions.append("embedding IS NULL")
        
    if doc_id is not None:
        conditions.append("document_id = :doc_id")
        params["doc_id"] = doc_id
        
    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
        
    limit_clause = ""
    if limit is not None:
        limit_clause = "LIMIT :limit"
        params["limit"] = limit
        
    sql_str = f"SELECT id, document_id, chunk_text FROM chunks {where_clause} ORDER BY document_id, chunk_index {limit_clause}"
    sql = text(sql_str)
    
    chunks = []
    with engine.connect() as conn:
        result = conn.execute(sql, params).fetchall()
        for row in result:
            chunks.append({
                "id": row[0],
                "document_id": row[1],
                "chunk_text": row[2]
            })
            
    return chunks


def _pgvector_literal(vec: list[float], decimals: int = 8) -> str:
    """
    Convert a Python list[float] into a pgvector-compatible literal string:
    "[0.12345678,-0.00001234,...]"
    - avoids scientific notation
    - removes spaces
    - replaces NaN/Inf with 0.0
    """
    parts = []
    for x in vec:
        if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
            x = 0.0
        # fixed-point formatting prevents scientific notation
        parts.append(f"{float(x):.{decimals}f}")
    return "[" + ",".join(parts) + "]"

def update_chunk_embeddings(chunk_embeddings: List[tuple[int, list[float]]]):
    if not chunk_embeddings:
        return

    sql = text("UPDATE chunks SET embedding = CAST(:embedding AS vector) WHERE id = :chunk_id")

    with engine.begin() as conn:
        for chunk_id, embedding_vector in chunk_embeddings:
            conn.execute(
                sql,
                {
                    "chunk_id": chunk_id,
                    "embedding": _pgvector_literal(embedding_vector),
                },
            )