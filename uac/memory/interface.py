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
        max_recent_steps = 5,
        recent_history = None
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
        self.hidden_state: str = 'This is the character in Red Dead Redemption 2.'
        self.max_recent_steps = max_recent_steps

        if recent_history:
            self.recent_history = recent_history
        else:
            self.recent_history = {"image": [], "skill": [], "decision_making_reasoning": [], "success_detection_reasoning": [], "reflection_reasoning": []}


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

    def add_recent_history(
        self,
        key: str,
        info: Any,
    ) -> None:
        """Add recent info (skill/image/reasoning) to memory."""
        self.recent_history[key].append(info)
        if len(self.recent_history[key]) > self.max_recent_steps:
            self.recent_history[key].pop(0)

    def get_recent_history(
        self,
        key: str,
        k: int = 1,
    ) -> List[Any]:
        """Query recent info (skill/image/reasoning) from memory."""
        assert len(self.recent_history[key]) > 0, f"No {key} history found."
        return self.recent_history[key][-k:] if len(self.recent_history[key]) >= k else self.recent_history[key]
    
    def add_experiences(self, data: Dict[str, Union[str, Image]]) -> None:
        """Add experiences to memory."""
        self.memory.add(data = data)

    def get_similar_experiences(self, data : str, top_k: int) -> List[Dict]:
        """Query the top-k experiences that are most similar to data."""
        return self.memory.similarity_search(data = data, top_k = top_k)

    def get_recent_experiences(self, recent_k: int) -> List[Dict]:
        """Query the recent k experiences."""
        return self.memory.recent_search(recent_k = recent_k)
    
    def add_hidden_state(self, hidden_state: str) -> None:
        """Update the hidden_state."""
        self.hidden_state = hidden_state
    
    def get_hidden_state(self) -> str:
        """Query the hidden_state."""
        return self.hidden_state

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
