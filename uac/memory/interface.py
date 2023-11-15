from typing import (
    Any,
    List,
    Dict,
    Union,
    Tuple,
)
from dataclasses import dataclass, fields

from uac.config import Config
from uac.log import Logger
from uac.provider.base_embedding import EmbeddingProvider
from uac.memory.base import VectorStore, Image
from uac.planner.helper import GatherInformationOutput

cfg = Config()
logger = Logger()


class MemoryInterface:
    def __init__(
        self,
        memory_path: str,
        vectorstores: Dict[str, VectorStore],
        embedding_provider: EmbeddingProvider,
    ) -> None:
        # self.short_term_memory = ShortNode(
        #     memory_path=memory_path,
        #     vectorstores=vectorstores,
        #     embedding_provider=embedding_provider,
        # )
        self.current_status: str = ""

    def add_gathered_info(
        self,
        info: GatherInformationOutput,
    ) -> None:
        """Add gathered information to memory."""
        # currently we only store description for the simplest retrieval
        self.current_status = info.description
        # self.short_term_memory.add(info)

    def get_current_status(self) -> str:
        """Query current status of the player."""
        return self.current_status

    def load_local(
        self,
        memory_path: str,
        vectorstore: Dict[str, VectorStore],
        embedding_provider: EmbeddingProvider,
    ) -> None:
        """Load the memory from the local file."""
        raise NotImplementedError

    def save_local(self) -> None:
        """Save the memory to the local file."""
        raise NotImplementedError
