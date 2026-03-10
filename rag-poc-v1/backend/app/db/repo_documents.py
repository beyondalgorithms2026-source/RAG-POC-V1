from sqlalchemy import text
from app.db.db import engine
from typing import Optional, List, Dict
from dataclasses import dataclass
from datetime import date

@dataclass
class DocumentRow:
    id: int
    file_path: str
    file_name: str
    hash_sha256: str
    chunked_hash_sha256: Optional[str] = None

def get_document_by_path(file_path: str) -> Optional[DocumentRow]:
    sql = text("SELECT id, file_path, file_name, hash_sha256, chunked_hash_sha256 FROM documents WHERE file_path = :file_path")
    with engine.connect() as conn:
        result = conn.execute(sql, {"file_path": file_path}).first()
        if result:
            return DocumentRow(
                id=result[0], 
                file_path=result[1], 
                file_name=result[2], 
                hash_sha256=result[3],
                chunked_hash_sha256=result[4]
            )
        return None

def upsert_document(file_path: str, file_name: str, doc_type: str, contract_date: Optional[date] = None, hash_sha256: str = ""):
    sql = text("""
        INSERT INTO documents (file_path, file_name, doc_type, contract_date, hash_sha256)
        VALUES (:file_path, :file_name, :doc_type, :contract_date, :hash_sha256)
        ON CONFLICT (file_path) DO UPDATE 
        SET file_name = EXCLUDED.file_name,
            doc_type = EXCLUDED.doc_type,
            contract_date = EXCLUDED.contract_date,
            hash_sha256 = EXCLUDED.hash_sha256,
            created_at = now()
        RETURNING id
    """)
    with engine.begin() as conn:
        result = conn.execute(sql, {
            "file_path": file_path,
            "file_name": file_name,
            "doc_type": doc_type,
            "contract_date": contract_date,
            "hash_sha256": hash_sha256
        })
        return result.scalar()

def get_all_documents() -> List[DocumentRow]:
    sql = text("SELECT id, file_path, file_name, hash_sha256, chunked_hash_sha256 FROM documents")
    docs = []
    with engine.connect() as conn:
        result = conn.execute(sql).fetchall()
        for row in result:
            docs.append(DocumentRow(
                id=row[0], 
                file_path=row[1], 
                file_name=row[2], 
                hash_sha256=row[3],
                chunked_hash_sha256=row[4]
            ))
    return docs

def update_document_chunked_hash(document_id: int, hash_sha256: str):
    sql = text("UPDATE documents SET chunked_hash_sha256 = :hash_sha256 WHERE id = :id")
    with engine.begin() as conn:
        conn.execute(sql, {"hash_sha256": hash_sha256, "id": document_id})
