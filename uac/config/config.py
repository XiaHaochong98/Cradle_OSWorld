import os
import time
from pathlib import Path

from dotenv import load_dotenv

from uac.utils import Singleton
from uac.utils.file_utils import assemble_project_path, get_project_root

import pyautogui

load_dotenv(verbose=True)


class Config(metaclass=Singleton):
    """
    Configuration class.
    """

    root_dir = '.'
    work_dir = './runs'
    log_dir = './logs'

    bootstrap_skill_library_path = './res/skills/bootstrap_library.dat'

    env_name = "Red Dead Redemption 2"

    def __init__(self) -> None:
        """Initialize the Config class"""
        self.debug_mode = False
        self.continuous_mode = False
        self.continuous_limit = 0

        # Base resolution and region for the game in 4k, used for angle scaling
        self.base_resolution = (3840, 2160)
        self.base_minimap_region = (112, 1450, 640, 640)

        # Full screen resolution for normalizing mouse movement
        self.screen_resolution = pyautogui.size()
        self.mouse_move_factor = self.screen_resolution[0] / self.base_resolution[0]

        # Default LLM parameters
        self.temperature = float(os.getenv("TEMPERATURE", "1"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1024"))

        # Sample framework parameters
        self.memory_backend = os.getenv("MEMORY_BACKEND", "local")

        self._set_dirs()
        self._set_game_window_info()

    def set_continuous_mode(self, value: bool) -> None:
        """Set the continuous mode value."""
        self.continuous_mode = value

    def _set_dirs(self) -> None:
        """Setup directories needed for one system run."""
        self.root_dir = get_project_root()

        self.work_dir = assemble_project_path(os.path.join(self.work_dir, str(time.time())))
        Path(self.work_dir).mkdir(parents=True, exist_ok=True)

        self.log_dir = assemble_project_path(self.log_dir)
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)

    def _set_game_window_info(self):

        game_window = pyautogui.getWindowsWithTitle(self.env_name)[0]
        assert game_window.width >= 1920 and game_window.height >= 1080, 'The resolution of screen should at least be 1920 X 1080.'
        assert game_window.width * 9 == game_window.height * 16, 'The screen ratio should be 16:9.'

        self.game_resolution = (game_window.width, game_window.height)
        self.game_region = (game_window.left, game_window.top, game_window.width, game_window.height)
        self.resolution_ratio = self.game_resolution[0] / self.base_resolution[0]
        self.minimap_region = self._calc_minimap_region(self.game_resolution)
        self.minimap_region[0] += game_window.left
        self.minimap_region[1] += game_window.top
        self.minimap_region = tuple(self.minimap_region)

    def _calc_minimap_region(self, screen_region):
        return [int(x * self.resolution_ratio ) for x in self.base_minimap_region]

