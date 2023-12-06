from typing import (
    Any,
    List,
    Dict,
    Union,
    Tuple,
)

from uac.config import Config
from uac.log import Logger
from uac.provider.base_embedding import EmbeddingProvider
from uac.memory.base import VectorStore, Image
from uac.memory import BasicMemory
from uac.memory.short_term_memory import ConversationMemory
from uac.agent import GatherInformationOutput, DecisionMakingOutput


config = Config()
logger = Logger()


class MemoryInterface:
    def __init__(
        self,
        memory_path: str,
        vectorstores: Dict[str, Dict[str, VectorStore]],
        embedding_provider: EmbeddingProvider,
    ) -> None:


        self.memory = BasicMemory(memory_path = memory_path, 
                                   vectorstores = vectorstores["basic_memory"], 
                                   embedding_provider = embedding_provider)  

        self.decision_making_memory = ConversationMemory(
            memory_path=memory_path,
            vectorstores=vectorstores["decision_making"],
            embedding_provider=embedding_provider,
        )
        self.success_detection_memory = ConversationMemory(
            memory_path=memory_path,
            vectorstores=vectorstores["success_detection"],
            embedding_provider=embedding_provider,
        )

        self.current_status: str = ""
        self.action_history: List[str] = []
        self.prev_reasoning: List[str] = []

    def add_gathered_info(
        self,
        info: GatherInformationOutput,
    ) -> None:
        """Add gathered information to memory."""
        # currently we only store description for the simplest retrieval
        self.current_status = info.description

    def get_current_status(self) -> str:
        """Query current status of the player."""
        return self.current_status

    def add_decision_making(
        self,
        decision_making_input: Dict[str, Any],
        decision_making_output: Dict[str, Any],
    ) -> None:
        self.decision_making_memory.add(
            messages=decision_making_input,
            response=decision_making_output,
        )

    def get_decision_making_examples(
        self,
        decision_making_input: Dict[str, Any],
    ) -> List[Union[str, Image]]:
        """Retrieve examples from memory for decision making."""
        return self.decision_making_memory.similarity_search(
            query=decision_making_input,
            # top_k=config.memory.decision_making.top_k,
        )

    def add_success_detection(
        self,
        success_detection_input: Dict[str, Any],
        success_detection_output: Dict[str, Any],
    ) -> None:
        self.success_detection_memory.add(
            messages=success_detection_input,
            response=success_detection_output,
        )

    def get_success_detection_examples(
        self,
        success_detection_input: Dict[str, Any],
    ) -> List[Union[str, Image]]:
        """Retrieve examples from memory for success detection."""
        return self.success_detection_memory.similarity_search(
            query=success_detection_input,
            # top_k=config.memory.success_detection.top_k,
        )

    def add_history(
        self,
        info: Dict[str, Any],
    ) -> None:
        """Add previous action and reasoning to memory."""
        self.action_history.append(info["skill"])
        self.prev_reasoning.append(info["reasoning"])

    def get_prev_action(self, k: int = 1) -> List[str]:
        """Query the previous action of the player."""
        assert len(self.action_history) > 0, "No action history found."
        return self.action_history[-k:] if len(self.action_history) >= k else self.action_history

    def get_prev_reasoning(self, k: int = 1) -> List[str]:
        """Query the previous reasoning of the player."""
        assert len(self.prev_reasoning) > 0, "No reasoning history found."
        return self.prev_reasoning[-k:] if len(self.prev_reasoning) >= k else self.prev_reasoning
    
    def add_experiences(self, data: Dict[str, Union[str, Image]]) -> None:
        """Add experiences to memory."""
        self.memory.add(data = data)

    def get_similar_experiences(self, data : str, top_k: int) -> List[Dict]:
        """Query the top-k experiences that are most similar to data."""
        return self.memory.similarity_search(data = data, top_k = top_k)

    def get_recent_experiences(self, recent_k: int) -> List[Dict]:
        """Query the recent k experiences."""
        return self.memory.recent_search(recent_k = recent_k)


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
