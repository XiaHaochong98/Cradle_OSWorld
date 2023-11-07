"""Base class for model providers."""
import abc

from typing import (
    List,
    Dict,
    Tuple,
    Optional,
)

from uac.config import Config
from uac.utils import AbstractSingleton

cfg = Config()


class LLMProviderSingleton(AbstractSingleton):
    @abc.abstractmethod
    def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        stop_tokens: Optional[List[str]] = None,
    ) -> Tuple[str, Dict[str, int]]:
        pass

    @abc.abstractmethod
    def init_provider(self, provider_cfg) -> None:
        pass
