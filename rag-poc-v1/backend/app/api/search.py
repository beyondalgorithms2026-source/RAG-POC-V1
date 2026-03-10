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
    distance: float
    rerank_score: Optional[float] = None

class SearchResponse(BaseModel):
    results: List[SearchResultItem]
    latency_ms: int

from fastapi import APIRouter
from app.retrieval.search import perform_search

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
def search_endpoint(request: SearchRequest):
    return perform_search(request)
