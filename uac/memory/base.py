import abc
from typing import (
    Any,
    Iterable,
    List,
    Dict,
    Union,
    Tuple,
    Optional,
)

from uac.config.config import Config
from uac.provider.base_embedding import EmbeddingProvider

config = Config()

Image = Any


class VectorStore(abc.ABC):
    """Interface for vector store."""

    @abc.abstractmethod
    def add_embeddings(
        self,
        keys: List[str],
        embeddings: Iterable[List[float]],
        **kwargs: Any,
    ) -> None:
        """Add embeddings to the vectorstore.

        Args:
            keys: list of metadatas associated with the embedding.
            embeddings: Iterable of embeddings to add to the vectorstore.
            kwargs: vectorstore specific parameters
        """

    @abc.abstractmethod
    def delete(self, keys: List[str] = None, **kwargs: Any) -> bool:
        """Delete by keys.

        Args:
            keys: List of keys to delete.
            **kwargs: Other keyword arguments that subclasses might use.

        Returns:
            bool: True if deletion is successful,
            False otherwise, None if not implemented.
        """

    @abc.abstractmethod
    def similarity_search(
        self,
        embedding: List[float],
        top_k: int,
        **kwargs: Any,
    ) -> List[Tuple[str, float]]:
        """Return keys most similar to query."""

    @abc.abstractmethod
    def save_local(self, name: str) -> None:
        """Save FAISS index and index_to_key to disk."""


class BaseMemory:
    """Base class for all memories."""

    @abc.abstractmethod
    def add(
        self,
        **kwargs,
    ) -> None:
        """Add data to memory.

        Args:
            **kwargs: Other keyword arguments that subclasses might use.
        """
        pass

    @abc.abstractmethod
    def similarity_search(
        self,
        data: Union[str, Image],
        top_k: int,
        **kwargs: Any,
    ) -> List[Union[str, Image]]:
        """Retrieve the keys from the vectorstores.

        Args:
            data: the query data.
            top_k: the number of results to return.
            **kwargs: Other keyword arguments that subclasses might use.

        Returns:
            the corresponding values from the memory.
        """
