import json
import logging
import os
import time
import sys

from colorama import Fore, Back, Style, init as colours_on

from uac.utils import Singleton
from uac.config import Config

config = Config()
colours_on(autoreset=True)


class ColorFormatter(logging.Formatter):
    # Change your colours here. Should use extra from log calls.
    COLORS = {
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "DEBUG": Fore.GREEN,
        "INFO": Fore.WHITE,
        "CRITICAL": Fore.RED + Back.WHITE
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        if color:
            record.name = color + record.name
            record.msg = record.msg + Style.RESET_ALL
        return logging.Formatter.format(self, record)


class Logger(metaclass=Singleton):

    log_file = 'uac.log'

    def __init__(self):
        self.to_file = False
        self._configure_root_logger()


    def _configure_root_logger(self):

        format = f'%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        formatter = logging.Formatter(format)
        c_formatter = ColorFormatter(format)

        stdout_handler = logging.StreamHandler(sys.stdout)
        # stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setLevel(logging.INFO)
        stdout_handler.setFormatter(c_formatter)

        stderr_handler = logging.StreamHandler()
        stderr_handler.setLevel(logging.ERROR)
        stderr_handler.setFormatter(c_formatter)

        file_handler = logging.FileHandler(filename=os.path.join(config.log_dir, self.log_file), mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        logging.basicConfig(level=logging.DEBUG, handlers=[stdout_handler, stderr_handler, file_handler])
        self.logger = logging.getLogger("UAC Logger")


    def _log(
            self,
            title="", 
            title_color=Fore.WHITE, 
            message="", 
            level=logging.INFO
        ):

        if message:
            if isinstance(message, list):
                message = " ".join(message)

        self.logger.log(level, message, extra={"title": title, "color": title_color})

    def critical(
            self, 
            message, 
            title=""
        ):

        self._log(title, Fore.RED + Back.WHITE, message, logging.ERROR)

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
            title_color=Fore.GREEN,
        ):

        self._log(title, title_color, message, logging.DEBUG)

    def write(
            self,
            message="",
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


    def error_ex(self, exception: Exception):
        traceback = exception.__traceback__
        while traceback:
            self.error("{}: {}".format(traceback.tb_frame.f_code.co_filename, traceback.tb_lineno))
            traceback = traceback.tb_next