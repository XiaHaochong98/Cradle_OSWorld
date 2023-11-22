from ahk import AHK

from uac.utils import Singleton


class IOEnvironment(metaclass=Singleton):
    """
    Wrapper for resources to interact with the game to make sure it's available where needed and multiple instances are not created.
    """

    def __init__(self) -> None:
        """Initialize the IO environment class"""
        self.ahk = AHK()
