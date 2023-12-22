from collections import namedtuple
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from colorama import Fore, Style, init as colours_on

from uac.utils import Singleton
from uac.utils.file_utils import assemble_project_path, get_project_root

import pyautogui

load_dotenv(verbose=True)


class Config(metaclass=Singleton):
    """
    Configuration class.
    """

    DEFAULT_GAME_RESOLUTION = (1920, 1080)
    DEFAULT_GAME_SCREEN_RATIO = (16, 9)

    DEFAULT_TEMPERATURE = 1.0
    DEFAULT_SEED = None

    DEFAULT_FIXED_SEED_VALUE = 42
    DEFAULT_FIXED_TEMPERATURE_VALUE = 0.0

    DEFAULT_POST_ACTION_WAIT_TIME = 3

    DEFAULT_MESSAGE_CONSTRUCTION_MODE = "tripartite"

    root_dir = '.'
    work_dir = './runs'
    log_dir = './logs'

    bootstrap_skill_library_path = './res/skills/bootstrap_library.dat'

    env_name = "Red Dead Redemption 2"

    # config for frame extraction
    VideoFrameExtractor_path = "./res/tool/subfinder/VideoSubFinderWXW.exe"
    VideoFrameExtractor_placeholderfile_path = "./res/tool/subfinder/test.srt"



    def __init__(self) -> None:
        """Initialize the Config class"""

        self.debug_mode = False
        self.continuous_mode = False
        self.continuous_limit = 0

        self.temperature = self.DEFAULT_TEMPERATURE
        self.seed = self.DEFAULT_SEED
        self.fixed_seed = False

        if self.fixed_seed:
            self.set_fixed_seed()

        # Base resolution and region for the game in 4k, used for angle scaling
        self.base_resolution = (3840, 2160)
        self.base_minimap_region = (112, 1450, 640, 640)

        # Full screen resolution for normalizing mouse movement
        self.screen_resolution = pyautogui.size()
        self.mouse_move_factor = self.screen_resolution[0] / self.base_resolution[0]

        # Default LLM parameters
        self.temperature = float(os.getenv("TEMPERATURE", self.temperature))	
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1024"))

        # Sample framework parameters
        self.memory_backend = os.getenv("MEMORY_BACKEND", "local")

        self._set_dirs()
        self._set_game_window_info()


    def set_fixed_seed(self, is_fixed: bool = True, seed: int = DEFAULT_FIXED_SEED_VALUE, temperature: float = DEFAULT_FIXED_TEMPERATURE_VALUE) -> None:
        """Set the fixed seed values. By default, used the default values. Please avoid using different values."""
        self.fixed_seed = is_fixed
        self.seed = seed
        self.temperature = temperature


    def set_continuous_mode(self, value: bool) -> None:
        """Set the continuous mode value."""
        self.continuous_mode = value


    def _set_dirs(self) -> None:
        """Setup directories needed for one system run."""
        self.root_dir = get_project_root()

        self.work_dir = assemble_project_path(os.path.join(self.work_dir, str(time.time())))
        Path(self.work_dir).mkdir(parents=True, exist_ok=True)

        self.log_dir = os.path.join(self.work_dir, self.log_dir)
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)


    def _set_game_window_info(self):

        named_windows = pyautogui.getWindowsWithTitle(self.env_name)

        # Fake game window info for testing cases with no running game
        game_window = namedtuple('A', ['top', 'left', 'width', 'height'])
        game_window.top = 0
        game_window.left = 0
        game_window.width = self.DEFAULT_GAME_RESOLUTION[0]
        game_window.height = self.DEFAULT_GAME_RESOLUTION[1]

        if len(named_windows) == 0:
            self._config_warn(f'-----------------------------------------------------------------')
            self._config_warn(f'Cannot find the env window. Assuming this is an offline test run!')
            self._config_warn(f'-----------------------------------------------------------------')
        else:
            game_window = named_windows[0]
            assert game_window.width >= self.DEFAULT_GAME_RESOLUTION[0] and game_window.height >= self.DEFAULT_GAME_RESOLUTION[1], 'The resolution of screen should at least be 1920 X 1080.'
            assert game_window.width * self.DEFAULT_GAME_SCREEN_RATIO[1] == game_window.height * self.DEFAULT_GAME_SCREEN_RATIO[0], 'The screen ratio should be 16:9.'

        self.game_resolution = (game_window.width, game_window.height)
        self.game_region = (game_window.left, game_window.top, game_window.width, game_window.height)
        self.resolution_ratio = self.game_resolution[0] / self.base_resolution[0]
        self.minimap_region = self._calc_minimap_region(self.game_resolution)
        self.minimap_region[0] += game_window.left
        self.minimap_region[1] += game_window.top
        self.minimap_region = tuple(self.minimap_region)


    def _calc_minimap_region(self, screen_region):
        return [int(x * self.resolution_ratio ) for x in self.base_minimap_region]


    def _config_warn(self, message):
        colours_on()
        print(Fore.RED + f' >>> WARNING: {message} ' + Style.RESET_ALL)
