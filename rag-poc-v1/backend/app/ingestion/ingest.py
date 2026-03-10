import os
import re
from datetime import datetime, date
from typing import Optional
from app.core.logging import logger
from app.core.config import settings
from app.ingestion.file_walker import get_supported_files
from app.ingestion.hashing import compute_sha256
from app.ingestion.parsers import parse_file
from app.ingestion.normalize import normalize_text
from app.db.repo_documents import get_document_by_path, upsert_document

def extract_date_from_filename(filename: str) -> Optional[date]:
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d").date()
        except ValueError:
            return None
    return None

def ingest_documents():
    data_dir = os.path.abspath(settings.DATA_DIR)
    extract_dir = os.path.abspath(settings.EXTRACT_DIR)
    
    files = get_supported_files(data_dir)
    logger.info(f"Found {len(files)} supported files in {data_dir}")
    
    stats = {"NEW": 0, "UPDATED": 0, "SKIPPED": 0, "FAILED": 0}
    failed_reasons = []
    
    for abs_path in files:
        file_name = os.path.basename(abs_path)
        
        try:
            try:
                parts = abs_path.split(os.sep)
                if 'data' in parts:
                    data_idx = parts.index('data')
                    rel_path = "/".join(parts[data_idx:])
                else:
                    rel_path = abs_path.replace(os.sep, '/')
            except Exception:
                rel_path = abs_path.replace(os.sep, '/')
                
            doc_type = os.path.splitext(file_name)[1].lower().strip('.')
            
            file_hash = compute_sha256(abs_path)
            
            existing_doc = get_document_by_path(rel_path)
            if existing_doc and existing_doc.hash_sha256 == file_hash:
                logger.info(f"SKIPPED: {file_name} (unchanged)")
                stats["SKIPPED"] += 1
                continue
                
            status = "UPDATED" if existing_doc else "NEW"
            
            contract_date = extract_date_from_filename(file_name)
            
            raw_text = parse_file(abs_path, doc_type)
            if not raw_text.strip():
                raise ValueError("no text extracted")
                
            clean_text = normalize_text(raw_text)
            
            out_filename = f"{file_hash}__{file_name}.txt"
            out_path = os.path.join(extract_dir, out_filename)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(clean_text)
                
            upsert_document(
                file_path=rel_path,
                file_name=file_name,
                doc_type=doc_type,
                contract_date=contract_date,
                hash_sha256=file_hash
            )
            
            logger.info(f"{status}: {file_name}")
            stats[status] += 1
            
        except Exception as e:
            logger.error(f"FAILED: {file_name} (Reason: {str(e)})")
            stats["FAILED"] += 1
            failed_reasons.append((file_name, str(e)))

    print("\n" + "="*40)
    print("INGESTION SUMMARY")
    print("="*40)
    print(f"NEW:     {stats['NEW']}")
    print(f"UPDATED: {stats['UPDATED']}")
    print(f"SKIPPED: {stats['SKIPPED']}")
    print(f"FAILED:  {stats['FAILED']}")
    print("="*40)
    if failed_reasons:
        print("FAILED FILES:")
        for idx, (fname, reason) in enumerate(failed_reasons[:20], 1):
            print(f"{idx}. {fname} - {reason}")
            
    logger.info(f"Ingestion summary: {stats}")
    return stats
