"""
Embedding generation service using Sentence Transformers
"""

from typing import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Generate text embeddings using a local Sentence Transformers model."""

    _instance: "EmbeddingService | None" = None

    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.device = settings.EMBEDDING_DEVICE
        self._model: SentenceTransformer | None = None

    @classmethod
    def get_instance(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name} on {self.device}")
            self._model = SentenceTransformer(self.model_name, device=self.device)
            logger.info("Embedding model loaded successfully")
        return self._model

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []
        embeddings = self.model.encode(
            list(texts),
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a single query string."""
        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return embedding.tolist()


embedding_service = EmbeddingService.get_instance()
