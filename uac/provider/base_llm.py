"""Base class for model providers."""
import abc

from uac.config import Config
from uac.utils import AbstractSingleton

cfg = Config()

class LLMProviderSingleton(AbstractSingleton):

    @abc.abstractmethod
    def create_completion(self, data):
        pass

    @abc.abstractmethod
    def init_provider(self, provider_cfg ) -> None:
        pass