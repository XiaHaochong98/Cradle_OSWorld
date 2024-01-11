from typing import (
    Any,
    List,
    Dict,
    Union,
    Tuple,
)
import os

from uac.config import Config
from uac.log import Logger
from uac.memory.base import BaseMemory, Image
from uac.utils.json_utils import load_json, save_json

config = Config()
logger = Logger()


class LocalMemory(BaseMemory):

    storage_filename = "memory.json"

    def __init__(
        self,
        memory_path: str = '',
        max_recent_steps: int = 5
    ) -> None:

        self.max_recent_steps = max_recent_steps
        self.memory_path = memory_path

        self.recent_history = {"image": [],
                               "action": [],
                               "decision_making_reasoning": [],
                               "success_detection_reasoning": [],
                               "self_reflection_reasoning": [],
                               "image_description":[],
                               "task_guidance":[],
                               "dialogue":[],
                               "task_description":[],
                               "skill_library":[],
                               "summarization":"The player is playing the game Red Dead Redemption for the PC."}


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

        #assert len(self.recent_history[key]) > 0, f"No {key} history found."
        if len(self.recent_history[key]) == 0:
            return [""]

        return self.recent_history[key][-k:] if len(self.recent_history[key]) >= k else self.recent_history[key]


    def add_summarization(self, summary: str) -> None:
        self.recent_history["summarization"] = summary


    def get_summarization(self) -> str:
        return self.recent_history["summarization"]


    def load(self) -> None:
        """Load the memory from the local file."""
        # @TODO load and store whole memory
        self.recent_history = load_json(os.path.join(self.memory_path, self.storage_filename))


    def save(self) -> None:
        """Save the memory to the local file."""
        # @TODO load and store whole memory
        save_json(file_path = os.path.join(self.memory_path, self.storage_filename), json_dict = self.recent_history, indent = 4)
