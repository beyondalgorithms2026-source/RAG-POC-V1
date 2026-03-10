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
            (c.embedding <=> CAST(:query_embedding AS vector)) AS distance,
            c.chunk_index
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
                "distance": float(row[9]),
                "chunk_index": row[10]
            })
            
    return results

def search_chunks_keyword(
    query_text: str, 
    k: int = 10, 
    doc_type: Optional[str] = None, 
    date_from: Optional[date] = None, 
    date_to: Optional[date] = None, 
    doc_id: Optional[int] = None
) -> List[Dict]:
    
    # Keyword query
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
            ts_rank_cd(c.search_tsv, websearch_to_tsquery('english', :query_text)) AS rank_score,
            c.chunk_index
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE c.search_tsv @@ websearch_to_tsquery('english', :query_text)
    """
    
    conditions = []
    params = {
        "query_text": query_text,
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
        
    # Order by rank DESC, then stable chunk_index
    sql_base += " ORDER BY rank_score DESC, c.chunk_index ASC LIMIT :k"
    
    sql = text(sql_base)
    results = []
    
    try:
        with engine.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
    except Exception:
        sql_fallback = text(sql_base.replace("websearch_to_tsquery", "plainto_tsquery"))
        with engine.connect() as conn:
            rows = conn.execute(sql_fallback, params).fetchall()
            
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
            "rank_score": float(row[9]),
            "chunk_index": row[10],
            "distance": None
        })
            
    return results
