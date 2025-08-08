import logging
from typing import List

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("sentence-transformers must be installed. Run 'pip install sentence-transformers'.")

logger = logging.getLogger(__name__)

# Module-level cache for the model
_model = None


def get_model():
    """
    Loads and caches the sentence-transformers/all-MiniLM-L6-v2 model.
    Returns:
        SentenceTransformer model instance.
    """
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers/all-MiniLM-L6-v2 model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def generate_embedding(text: str) -> List[float]:
    """
    Generates an embedding for the given text using all-MiniLM-L6-v2.
    Args:
        text: The input string to embed.
    Returns:
        List of floats representing the embedding vector.
    Raises:
        ValueError if text is empty or embedding fails.
    """
    if not text or not isinstance(text, str):
        logger.warning("Empty or invalid text provided for embedding.")
        raise ValueError("Text for embedding must be a non-empty string.")
    try:
        model = get_model()
        embedding = model.encode(text, show_progress_bar=False)
        return embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise ValueError(f"Embedding generation failed: {e}")