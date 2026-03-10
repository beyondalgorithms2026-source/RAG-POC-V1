from app.core.config import settings
from sentence_transformers import SentenceTransformer
from app.core.logging import logger

_model = None
_EXPECTED_DIM = None

def get_model():
    global _model, _EXPECTED_DIM
    if _model is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Calculate dynamic dimension size based on the model
        dummy_embedding = _model.encode(["test dummy"])[0]
        _EXPECTED_DIM = len(dummy_embedding)
        logger.info(f"Model loaded successfully. Expected vector dimensions: {_EXPECTED_DIM}")
        
    return _model

def get_expected_dim() -> int:
    get_model() # Ensure it's loaded
    return _EXPECTED_DIM

def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
        
    model = get_model()
    # normalize_embeddings=True is highly recommended for cosine similarity
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()
