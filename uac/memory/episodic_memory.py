from typing import (
    List,
    Dict,
    Union,
    Optional,
)

import json
import os

from uac.config import Config
from uac.log import Logger
from uac.provider.base_embedding import EmbeddingProvider
from uac.memory.base import VectorStore, BaseMemory, Image

cfg = Config()
logger = Logger()


class EpisodicMemory(BaseMemory):
    def __init__(
        self,
        memory_path: str,
        vectorstore: VectorStore,
        embedding_provider: EmbeddingProvider,
        memory: Optional[Dict] = None,
    ):
        super().__init__(memory_path, vectorstore, embedding_provider, memory)

    def add(
        self,
        data: Dict[str, Union[str, Image]],
    ) -> None:
        """Add data to memory.

        Args:
            data: the mapping from unique name (id) to text/image.
        """
        # TODO:
        # keys: List[str] = list(data.keys())
        # values: List[Union[str, Image]] = list(data.values())
        # embeddings = [self.embedding_provider.embed_query(v) for v in values]
        # for k, v in zip(keys, values):
        #     self.memory[k] = v
        # keys: str = data["instruction"]
        # screenshot: Image = data["screenshot"]
        # timestep: int = data["timestep"]
        # description: int = data["description"]
        # inventory: str = data["inventory"]
        # self.memory[k] = {
        #     "screenshot": screenshot,
        #     "timestep": timestep,
        #     "description": description,
        #     "inventory": inventory,
        # }
        # self.vectorstore.add_embeddings(keys, embeddings)

    def similarity_search(
        self,
        data: Union[str, Image],
        top_k: int = 3,
        **kwargs,
    ) -> List[Union[str, Image]]:
        """Retrieve the keys from the vectorstore.

        Args:
            data: the query data.
            top_k: the number of results to return.
            **kwargs: Other keyword arguments that subclasses might use.

        Returns:
            the corresponding values from the memory.
        """
        query_embedding = self.embedding_provider.embed_query(data)
        key_and_score = self.vectorstore.similarity_search(query_embedding, top_k)

        return [self.memory[k] for k, score in key_and_score]

    def periodic_summary(self) -> None:
        """Periodically summarize the memory."""
        pass

    @classmethod
    def load_local(
        cls,
        memory_path: str,
        vectorstore: VectorStore,
        embedding_provider: EmbeddingProvider,
    ) -> "EpisodicMemory":
        """Load the memory from the local file."""
        with open(os.path.join(memory_path, "memory.json"), "r") as rf:
            memory = json.load(rf)

        return cls(
            memory_path=memory_path,
            vectorstore=vectorstore,
            embedding_provider=embedding_provider,
            memory=memory,
        )

    def save_local(self) -> None:
        """Save the memory to the local file."""
        with open(os.path.join(self.memory_path, "memory.json"), "w") as f:
            json.dump(self.memory, f, indent=2)
        self.vectorstore.save_local()