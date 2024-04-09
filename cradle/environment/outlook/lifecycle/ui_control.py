import time
from typing import Any

from PIL import Image, ImageDraw, ImageFont
import mss
import mss.tools

from cradle.config import Config
from cradle.log import Logger
from cradle.gameio import IOEnvironment

config = Config()
logger = Logger()
io_env = IOEnvironment()

PAUSE_SCREEN_WAIT = 1


def pause_game():
    logger.warn("Pause doesn't apply to application!")


def unpause_game():
    logger.warn("Unpause doesn't apply to application!")


def switch_to_game():
    named_windows = io_env.get_windows_by_config()
    if len(named_windows) == 0:
        error_msg = f"Cannot find the game window {config.env_name}!"
        logger.error(error_msg)
        raise EnvironmentError(error_msg)
    else:
        try:
            named_windows[0].activate()
        except Exception as e:
            if "Error code from Windows: 0" in str(e):
                # Handle pygetwindow exception
                pass
            else:
                raise e

    time.sleep(1)
    unpause_game()
    time.sleep(1)


def take_screenshot(tid : float,
                    screen_region : tuple[int, int, int, int] = None,
                    minimap_region : tuple[int, int, int, int] = None,
                    include_minimap = True,
                    draw_axis = False):

    if screen_region is None:
        screen_region = config.env_region

    if minimap_region is None:
        minimap_region = config.base_minimap_region

    region = screen_region
    region = {
        "left": region[0],
        "top": region[1],
        "width": region[2],
        "height": region[3],
    }

    output_dir = config.work_dir

    # Save screenshots
    screen_image_filename = output_dir + "/screen_" + str(tid) + ".jpg"

    with mss.mss() as sct:
        screen_image = sct.grab(region)
        image = Image.frombytes("RGB", screen_image.size, screen_image.bgra, "raw", "BGRX")
        image.save(screen_image_filename)

    return screen_image_filename, None


def is_env_paused():

    is_paused = False

    logger.warn("Pause doesn't apply to application!")

    return is_paused


__all__ = [
    "pause_game",
    "unpause_game",
    "take_screenshot",
    "switch_to_game",
]