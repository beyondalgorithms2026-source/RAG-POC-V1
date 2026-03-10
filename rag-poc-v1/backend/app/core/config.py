import os
from pydantic_settings import BaseSettings

# Calculate paths relative to this file
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CORE_DIR)
BACKEND_DIR = os.path.dirname(APP_DIR)
REPO_ROOT = os.path.dirname(BACKEND_DIR)

ENV_FILE_PATH = os.path.join(BACKEND_DIR, ".env")

class Settings(BaseSettings):
    DATABASE_URL: str
    DATA_DIR: str = "../data/contracts"
    EXTRACT_DIR: str = "../data/extracted_text"
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_BATCH_SIZE: int = 32

    # LLM Settings (M6)
    LLM_PROVIDER: str = "ollama"
    LLM_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "gpt-oss:120b-cloud"
    LLM_TIMEOUT_S: int = 60
    OLLAMA_API_KEY: str = ""

    # Reranker Settings (M9)
    RERANK_ENABLED: bool = False
    RERANK_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    TOP_K_INITIAL: int = 30

    class Config:
        env_file = ENV_FILE_PATH
        env_file_encoding = "utf-8"

settings = Settings()

os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.EXTRACT_DIR, exist_ok=True)
