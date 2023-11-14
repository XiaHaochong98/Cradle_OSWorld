"""Base class for LLM model providers."""
import abc
from typing import (
    List,
    Dict,
    Tuple,
    Optional,
)

from uac.config import Config

cfg = Config()


class LLMProvider(abc.ABC):
    """Interface for LLM models."""

    @abc.abstractmethod
    def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        stop_tokens: Optional[List[str]] = None,
    ) -> Tuple[str, Dict[str, int]]:
        """Create a compeltion from messages in text (and potentially also encoded images)."""
        pass

    @abc.abstractmethod
    def init_provider(self, provider_cfg) -> None:
        """Initialize a provider via a json config."""
        pass
