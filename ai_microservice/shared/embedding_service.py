import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_model = None


def _load_model():
    global _model
    if _model is not None:
        return

    try:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        logger.exception("Failed to load embedding model")
        raise


def get_embedding(text: str) -> list[float]:
    _load_model()
    embedding = _model.encode(text)
    return embedding.tolist()
