from typing import Optional, List
from pydantic import BaseModel, Field
from app.api.search import SearchFilters

class AskRequest(BaseModel):
    question: str
    k_chunks: int = Field(default=6, le=20, description="Top N chunks to pull for context")
    filters: Optional[SearchFilters] = None
    dry_run: bool = Field(default=False, description="Returns the constructed prompt without calling the LLM")

class CitationItem(BaseModel):
    source_id: str
    chunk_id: int
    file_name: str
    heading: str
    section_path: str
    snippet: str

class AskResponse(BaseModel):
    answer: Optional[str] = None
    citations: List[CitationItem] = []
    used_chunks_count: int = 0
    latency_ms: int = 0
    debug_info: Optional[dict] = None

from fastapi import APIRouter, HTTPException
from app.llm.client import is_llm_ready
from app.core.config import settings

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
def ask_endpoint(request: AskRequest):
    if not request.dry_run and not is_llm_ready():
        raise HTTPException(
            status_code=503,
            detail={"error": "LLM not ready", "message": f"The configured LLM provider or model '{settings.LLM_MODEL}' is unreachable."}
        )
        
    from app.answering.ask import perform_ask
    return perform_ask(request)

