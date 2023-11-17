import os

from dotenv import load_dotenv

from uac.utils import Singleton

import pyautogui

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

        self.base_resolution = (3840, 2160)
        self.base_mini_map_region = (112, 1450, 640, 640)

        self.screen_resolution = pyautogui.size()
        self.mouse_move_factor = self.screen_resolution[0] / self.base_resolution[0]

        self.temperature = float(os.getenv("TEMPERATURE", "1"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1024"))

        self.memory_backend = os.getenv("MEMORY_BACKEND", "local")

        self.set_work_dir()
        self.set_game_window_info()

    def set_continuous_mode(self, value: bool) -> None:
        """Set the continuous mode value."""
        self.continuous_mode = value

    def set_work_dir(self) -> None:
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.dirname(path) # get to parent, outside of project code path
        self.work_dir = path

    def set_game_window_info(self):
        game_window = pyautogui.getWindowsWithTitle("Red Dead Redemption 2")[0]
        assert game_window.width >= 1920 and game_window.height >= 1080, 'The resolution of screen should at least be 1920 X 1080.'
        assert game_window.width * 9 == game_window.height * 16, 'The screen ratio should be 16:9.'

        self.game_resolution = (game_window.width, game_window.height)
        self.game_region = (game_window.left, game_window.top, game_window.width, game_window.height)
        self.mini_map_region = [int(x * (self.game_resolution[0] / self.base_resolution[0]) ) for x in self.base_mini_map_region]
        self.mini_map_region[0] += game_window.left
        self.mini_map_region[1] += game_window.top
        self.mini_map_region = tuple(self.mini_map_region)
