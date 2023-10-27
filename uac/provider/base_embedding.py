"""Base class for embedding model providers."""
import abc
from typing import (
    List,
)

from uac.config import Config

cfg = Config()


class EmbeddingProvider(abc.ABC):
    """Interface for embedding models."""

    @abc.abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""

    @abc.abstractmethod
    def get_embedding_dim(self) -> int:
        """Get the embedding dimension."""
        pass
