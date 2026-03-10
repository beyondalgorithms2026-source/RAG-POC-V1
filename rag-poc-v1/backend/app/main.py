from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.health import router as health_router
from .api.search import router as search_router
from .api.ask import router as ask_router
from .llm.client import verify_llm_ready
from .core.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not verify_llm_ready():
        logger.error("LLM Preflight failed. Ensure Ollama is running.")
    yield

app = FastAPI(title="RAG PoC v1 API", lifespan=lifespan)

# M7: Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["OPTIONS", "POST", "GET"], # OPTIONS needed for preflight
    allow_headers=["Content-Type"],
)

app.include_router(health_router)
app.include_router(search_router)
app.include_router(ask_router)
