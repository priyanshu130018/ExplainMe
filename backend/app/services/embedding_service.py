import os
import logging
import hashlib
from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract interface for generating text embeddings."""

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        pass


class SentenceTransformersEmbeddingProvider(EmbeddingProvider):
    """Sentence Transformers embeddings (e.g. all-MiniLM-L6-v2, 384 dimensions)."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model = None

    def _pseudo_embedding(self, text: str, dim: int = 384) -> List[float]:
        """Fast deterministic pseudo-embedding for testing or when model isn't pre-loaded."""
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16) % (2**32)
        np.random.seed(seed)
        vec = np.random.randn(dim)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def _get_model(self):
        # In test mode or when torch is absent, use instant pseudo-embeddings
        if os.getenv("PYTEST_CURRENT_TEST"):
            return None

        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.warning(f"[EmbeddingProvider] SentenceTransformer not available: {e}. Using deterministic fallback.")
        return self._model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        if model is not None:
            embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings.tolist()
        return [self._pseudo_embedding(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        model = self._get_model()
        if model is not None:
            emb = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return emb.tolist()
        return self._pseudo_embedding(text)
