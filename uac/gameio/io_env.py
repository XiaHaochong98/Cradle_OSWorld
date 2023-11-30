import os

from ahk import AHK

from uac.utils import Singleton
from uac.config import Config

config = Config()


class IOEnvironment(metaclass=Singleton):
    """
    Wrapper for resources to interact with the game to make sure it's available where needed and multiple instances are not created.
    """

    def __init__(self) -> None:
        """Initialize the IO environment class"""
        self.ahk = AHK()


    def list_session_screenshots(self, session_dir: str = config.work_dir):

        # List all files in dir starting with "screen"
        screenshots = [f for f in os.listdir(session_dir) if os.path.isfile(os.path.join(session_dir, f)) and f.startswith("screen")]

        # Sort list by creation time
        screenshots.sort(key=lambda x: os.path.getctime(os.path.join(session_dir, x)))

        return screenshots
