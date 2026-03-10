from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field

class SearchFilters(BaseModel):
    doc_type: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    doc_id: Optional[int] = None

class SearchRequest(BaseModel):
    question: str
    k: int = Field(default=10, le=50, description="Number of results to return, max 50")
    filters: Optional[SearchFilters] = None
    mode: Optional[str] = Field(default=None, description="'vector' | 'keyword' | 'hybrid'")
    debug: bool = False

class SearchResultItem(BaseModel):
    chunk_id: int
    document_id: int
    file_name: str
    file_path: str
    doc_type: str
    contract_date: Optional[date] = None
    heading: str
    section_path: str
    snippet: str
    score: float
    distance: Optional[float] = None
    rerank_score: Optional[float] = None
    vector_score: Optional[float] = None
    keyword_score: Optional[float] = None
    combined_score: Optional[float] = None
    rank_score: Optional[float] = None

class SearchResponse(BaseModel):
    results: List[SearchResultItem]
    latency_ms: int
    mode: str

from fastapi import APIRouter

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
def search_endpoint(request: SearchRequest):
    from app.retrieval.search import perform_search
    return perform_search(request)
