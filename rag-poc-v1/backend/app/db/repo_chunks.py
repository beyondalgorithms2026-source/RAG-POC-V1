from sqlalchemy import text
from app.db.db import engine
from typing import List, Dict

def check_chunks_exist(document_id: int) -> bool:
    sql = text("SELECT id FROM chunks WHERE document_id = :doc_id LIMIT 1")
    with engine.connect() as conn:
        result = conn.execute(sql, {"doc_id": document_id}).first()
        return result is not None

def delete_chunks_for_document(document_id: int):
    sql = text("DELETE FROM chunks WHERE document_id = :doc_id")
    with engine.begin() as conn:
        conn.execute(sql, {"doc_id": document_id})

def insert_chunks(document_id: int, chunks: List[Dict]):
    sql = text("""
        INSERT INTO chunks (document_id, chunk_index, heading, section_path, chunk_text, token_count)
        VALUES (:doc_id, :idx, :heading, :section_path, :text, :tokens)
    """)
    with engine.begin() as conn:
        for idx, chunk in enumerate(chunks):
            conn.execute(sql, {
                "doc_id": document_id,
                "idx": idx,
                "heading": chunk["heading"],
                "section_path": chunk["section_path"],
                "text": chunk["chunk_text"],
                "tokens": chunk["token_count"]
            })
