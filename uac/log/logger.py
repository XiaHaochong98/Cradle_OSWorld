import json
import logging
import os
import time

from colorama import Fore

from uac.config import Config
from uac.utils import Singleton

class Logger(metaclass=Singleton):

    def __init__(self):
        self.to_file = False

    def _log(
            self,
            title="", 
            title_color="", 
            message="", 
            level=logging.INFO
        ):

        if message:
            if isinstance(message, list):
                message = " ".join(message)
        self.logger.log(level, message, extra={"title": title, "color": title_color})

    def error(
            self, 
            message, 
            title=""
        ):

        self._log(title, Fore.RED, message, logging.ERROR)

    def debug(
        self,
        message,
        title="",
        title_color=Fore.WHITE,
        ):

        self._log(title, title_color, message, logging.DEBUG)

    def write(
        self,
        message,
        title="",
        title_color=Fore.WHITE,
        ):

        self._log(title, title_color, message, logging.INFO)

    def warn(
        self,
        message,
        title="",
        title_color=Fore.YELLOW,
        ):

        self._log(title, title_color, message, logging.WARN)