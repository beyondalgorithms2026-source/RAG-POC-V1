import time
from app.api.search import SearchRequest, SearchResponse, SearchResultItem
from app.embedding.embedder import embed_texts
from app.db.repo_search import search_chunks
from app.core.config import settings
from app.core.logging import logger

def perform_search(request: SearchRequest) -> SearchResponse:
    start_time = time.time()
    
    # 1. Embed the question
    try:
        query_vector = embed_texts([request.question])[0]
    except Exception as e:
        logger.error(f"Failed to embed question: {e}")
        return SearchResponse(results=[], latency_ms=int((time.time() - start_time) * 1000))
        
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
        
    # 3. Query DB — over-fetch if reranker is enabled
    effective_k = settings.TOP_K_INITIAL if settings.RERANK_ENABLED else request.k
    try:
        raw_results = search_chunks(
            query_vector=query_vector,
            k=effective_k,
            doc_type=doc_type,
            date_from=date_from,
            date_to=date_to,
            doc_id=doc_id
        )
    except Exception as e:
        logger.error(f"DB search failed: {e}")
        return SearchResponse(results=[], latency_ms=int((time.time() - start_time) * 1000))
    
    # 3b. Rerank if enabled
    if settings.RERANK_ENABLED and raw_results:
        from app.retrieval.reranker import rerank
        logger.info(f"Reranking {len(raw_results)} candidates down to {request.k}")
        raw_results = rerank(request.question, raw_results, request.k)
        
    # 4. Format results
    results = []
    for r in raw_results:
        distance = r["distance"]
        # Score mapping: max(0.0, 1.0 - distance) handles negative values safely
        score = max(0.0, 1.0 - distance)
        
        results.append(SearchResultItem(
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
            distance=round(distance, 4),
            rerank_score=round(r["rerank_score"], 4) if "rerank_score" in r else None
        ))
        
    latency_ms = int((time.time() - start_time) * 1000)
    
    return SearchResponse(
        results=results,
        latency_ms=latency_ms
    )
