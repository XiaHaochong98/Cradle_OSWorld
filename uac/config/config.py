import os

from dotenv import load_dotenv

from uac.utils import Singleton

load_dotenv(verbose=True)


class Config(metaclass=Singleton):
    """
    Configuration class.
    """

    def __init__(self) -> None:
        """Initialize the Config class"""
        self.debug_mode = False
        self.continuous_mode = False
        self.continuous_limit = 0

        self.llm_model = os.getenv("LLM_MODEL", "gpt-35-turbo")
        self.embedding_model = os.getenv("EMB_MODEL", "text-embedding-ada-002")
        
        self.temperature = float(os.getenv("TEMPERATURE", "1"))

        self.memory_backend = os.getenv("MEMORY_BACKEND", "local")

        self.set_work_dir()

    def set_continuous_mode(self, value: bool) -> None:
        """Set the continuous mode value."""
        self.continuous_mode = value

    def set_model_name(self, value: bool) -> None:
        self.model_name = value

    def set_model_path(self, value: bool) -> None:
        self.model_path = value

    def set_work_dir(self) -> None:
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.dirname(path) # get to parent, outside of project code path
        self.work_dir = path