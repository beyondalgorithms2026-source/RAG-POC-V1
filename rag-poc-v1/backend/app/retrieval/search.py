import time
from typing import List, Dict
from app.api.search import SearchRequest, SearchResponse, SearchResultItem
from app.embedding.embedder import embed_texts
from app.db.repo_search import search_chunks, search_chunks_keyword
from app.core.config import settings
from app.core.logging import logger

def merge_hybrid_results(
    vector_results: List[Dict], 
    keyword_results: List[Dict], 
    k: int, 
    alpha: float = 0.65
) -> List[Dict]:
    merged = {}
    
    # Process vector results
    for r in vector_results:
        chunk_id = r["chunk_id"]
        dist = r["distance"] if r["distance"] is not None else 1.0
        v_score = max(0.0, 1.0 - dist)
        
        merged[chunk_id] = {
            "chunk_id": chunk_id,
            "document_id": r["document_id"],
            "file_name": r["file_name"],
            "file_path": r["file_path"],
            "doc_type": r["doc_type"],
            "contract_date": r["contract_date"],
            "heading": r["heading"],
            "section_path": r["section_path"],
            "snippet": r["snippet"],
            "distance": dist,
            "chunk_index": r["chunk_index"],
            "vector_score": v_score,
            "keyword_score": 0.0,
            "rank_score": 0.0
        }
        
    # Process keyword results
    max_rank = max((r["rank_score"] for r in keyword_results), default=0.0)
    
    for r in keyword_results:
        chunk_id = r["chunk_id"]
        k_score = r["rank_score"] / max_rank if max_rank > 0 else 0.0
        
        if chunk_id in merged:
            merged[chunk_id]["keyword_score"] = k_score
            merged[chunk_id]["rank_score"] = r["rank_score"]
        else:
            merged[chunk_id] = {
                "chunk_id": chunk_id,
                "document_id": r["document_id"],
                "file_name": r["file_name"],
                "file_path": r["file_path"],
                "doc_type": r["doc_type"],
                "contract_date": r["contract_date"],
                "heading": r["heading"],
                "section_path": r["section_path"],
                "snippet": r["snippet"],
                "distance": None, 
                "chunk_index": r["chunk_index"],
                "vector_score": 0.0,
                "keyword_score": k_score,
                "rank_score": r["rank_score"]
            }
            
    # Calculate combined score
    final_results = []
    for r in merged.values():
        r["combined_score"] = alpha * r["vector_score"] + (1.0 - alpha) * r["keyword_score"]
        final_results.append(r)
        
    # Sort: combined DESC, distance ASC, chunk_index ASC (stable)
    final_results.sort(key=lambda x: (
        -x["combined_score"], 
        x["distance"] if x["distance"] is not None else float('inf'), 
        x["chunk_index"]
    ))
    
    return final_results[:k]

def perform_search(request: SearchRequest) -> SearchResponse:
    start_time = time.time()
    
    # 1. Determine Mode
    mode = request.mode
    if not mode:
        mode = "hybrid" if settings.HYBRID_ENABLED else "vector"
        
    # 2. Extract filters
    doc_type = None
    date_from = None
    date_to = None
    doc_id = None
    if request.filters:
        doc_type = request.filters.doc_type
        date_from = request.filters.date_from
        date_to = request.filters.date_to
        doc_id = request.filters.doc_id

    try:
        if mode == "vector":
            query_vector = embed_texts([request.question])[0]
            effective_k = settings.TOP_K_INITIAL if settings.RERANK_ENABLED else request.k
            raw_results = search_chunks(
                query_vector=query_vector, k=effective_k, 
                doc_type=doc_type, date_from=date_from, date_to=date_to, doc_id=doc_id
            )
            for r in raw_results:
                r["vector_score"] = max(0.0, 1.0 - (r["distance"] or 1.0))
                r["keyword_score"] = None
                r["combined_score"] = None
                r["rank_score"] = None
                
        elif mode == "keyword":
            effective_k = settings.TOP_K_INITIAL if settings.RERANK_ENABLED else request.k
            raw_results = search_chunks_keyword(
                query_text=request.question, k=effective_k,
                doc_type=doc_type, date_from=date_from, date_to=date_to, doc_id=doc_id
            )
            max_rank = max((r["rank_score"] for r in raw_results), default=0.0)
            for r in raw_results:
                r["keyword_score"] = r["rank_score"] / max_rank if max_rank > 0 else 0.0
                r["vector_score"] = None
                r["combined_score"] = None
                
        elif mode == "hybrid":
            query_vector = embed_texts([request.question])[0]
            v_k = settings.VECTOR_CANDIDATES
            k_k = settings.KEYWORD_CANDIDATES
            effective_k = settings.TOP_K_INITIAL if settings.RERANK_ENABLED else request.k
            
            vector_res = search_chunks(
                query_vector=query_vector, k=v_k,
                doc_type=doc_type, date_from=date_from, date_to=date_to, doc_id=doc_id
            )
            keyword_res = search_chunks_keyword(
                query_text=request.question, k=k_k,
                doc_type=doc_type, date_from=date_from, date_to=date_to, doc_id=doc_id
            )
            
            raw_results = merge_hybrid_results(
                vector_results=vector_res,
                keyword_results=keyword_res,
                k=effective_k,
                alpha=settings.HYBRID_ALPHA
            )
        else:
            raw_results = []
            
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return SearchResponse(results=[], latency_ms=int((time.time() - start_time) * 1000), mode=mode)
        
    # 3. Rerank if enabled (applies to all modes)
    if settings.RERANK_ENABLED and raw_results:
        from app.retrieval.reranker import rerank
        logger.info(f"Reranking {len(raw_results)} candidates down to {request.k}")
        raw_results = rerank(request.question, raw_results, request.k)
        
    # 4. Format results
    results = []
    for r in raw_results:
        # Final primary score is what?
        if mode == "vector":
            score = max(0.0, 1.0 - (r["distance"] or 1.0))
        elif mode == "keyword":
            score = r.get("keyword_score", 0.0)
        else:
            score = r.get("combined_score", 0.0)
            
        item = SearchResultItem(
            chunk_id=r["chunk_id"],
            document_id=r["document_id"],
            file_name=r["file_name"],
            file_path=r["file_path"],
            doc_type=r["doc_type"],
            contract_date=r["contract_date"],
            heading=r["heading"],
            section_path=r["section_path"],
            snippet=r["snippet"],
            score=round(score, 4),
            distance=round(r["distance"], 4) if r.get("distance") is not None else None,
            rerank_score=round(r["rerank_score"], 4) if "rerank_score" in r else None
        )
        
        if request.debug:
            item.vector_score = round(r["vector_score"], 4) if r.get("vector_score") is not None else None
            item.keyword_score = round(r["keyword_score"], 4) if r.get("keyword_score") is not None else None
            item.combined_score = round(r["combined_score"], 4) if r.get("combined_score") is not None else None
            item.rank_score = round(r["rank_score"], 4) if r.get("rank_score") is not None else None
            
        results.append(item)
        
    latency_ms = int((time.time() - start_time) * 1000)
    
    return SearchResponse(
        results=results,
        latency_ms=latency_ms,
        mode=mode
    )
