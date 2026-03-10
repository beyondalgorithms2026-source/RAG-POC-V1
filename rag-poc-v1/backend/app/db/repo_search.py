from sqlalchemy import text
from app.db.db import engine
from typing import List, Dict, Optional
from datetime import date
from app.db.repo_embeddings import _pgvector_literal

def search_chunks(
    query_vector: list[float], 
    k: int = 10, 
    doc_type: Optional[str] = None, 
    date_from: Optional[date] = None, 
    date_to: Optional[date] = None, 
    doc_id: Optional[int] = None
) -> List[Dict]:
    
    # Base query
    sql_base = """
        SELECT 
            c.id AS chunk_id,
            c.document_id,
            d.file_name,
            d.file_path,
            d.doc_type,
            d.contract_date,
            c.heading,
            c.section_path,
            c.chunk_text,
            (c.embedding <=> CAST(:query_embedding AS vector)) AS distance
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE c.embedding IS NOT NULL
    """
    
    conditions = []
    params = {
        "query_embedding": _pgvector_literal(query_vector),
        "k": k
    }
    
    if doc_type:
        conditions.append("d.doc_type = :doc_type")
        params["doc_type"] = doc_type
        
    if date_from:
        conditions.append("d.contract_date >= :date_from")
        params["date_from"] = date_from
        
    if date_to:
        conditions.append("d.contract_date <= :date_to")
        params["date_to"] = date_to
        
    if doc_id is not None:
        conditions.append("d.id = :doc_id")
        params["doc_id"] = doc_id
        
    if conditions:
        sql_base += " AND " + " AND ".join(conditions)
        
    # Order by cosine distance ASC (smaller is closer), then stable chunk_index
    sql_base += " ORDER BY distance ASC, c.chunk_index ASC LIMIT :k"
    
    sql = text(sql_base)
    results = []
    
    with engine.connect() as conn:
        rows = conn.execute(sql, params).fetchall()
        for row in rows:
            results.append({
                "chunk_id": row[0],
                "document_id": row[1],
                "file_name": row[2],
                "file_path": row[3],
                "doc_type": row[4],
                "contract_date": row[5],
                "heading": row[6],
                "section_path": row[7],
                "snippet": row[8],
                "distance": float(row[9])
            })
            
    return results
