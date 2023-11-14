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

        self.default_game_resolution = (2560, 1440)
        self.game_resolution = self.default_game_resolution
        self.base_resolution = (3840, 2160)
        self.mouse_move_factor = self.game_resolution[0] / self.base_resolution[0]

        self.temperature = float(os.getenv("TEMPERATURE", "1"))

        self.memory_backend = os.getenv("MEMORY_BACKEND", "local")

        self.set_work_dir()

    def set_continuous_mode(self, value: bool) -> None:
        """Set the continuous mode value."""
        self.continuous_mode = value

    def set_work_dir(self) -> None:
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.dirname(path) # get to parent, outside of project code path
        self.work_dir = path