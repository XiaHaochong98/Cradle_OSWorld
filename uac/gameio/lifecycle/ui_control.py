import os
import time

import pydirectinput
import pyautogui
from PIL import Image, ImageDraw, ImageFont

from uac.config import Config
from uac.log import Logger
from uac.utils.template_matching import match_template_image

config = Config()
logger = Logger()


def pause_game():
    if not is_env_paused():
        pydirectinput.press('esc')
    else:
        logger.debug("The environment is already paused!")
    time.sleep(1)


def unpause_game():
    if is_env_paused():
        pydirectinput.press('esc')
    else:
        logger.debug("The environment is not paused!")
    time.sleep(1)


def switch_to_game():
    pyautogui.getWindowsWithTitle(config.env_name)[0].activate()
    time.sleep(1)
    unpause_game()
    time.sleep(1)


def switch_to_code():
    pause_game()
    pyautogui.hotkey("ctrl", "win", "right") # switch desktop


def take_screenshot(tid : float = 0.0,
                    screen_region : tuple[int, int, int, int] = config.game_region,
                    minimap_region : tuple[int, int, int, int] = config.minimap_region,
                    include_minimap = True,
                    draw_axis = False):
    
    output_dir = config.work_dir

    # save screenshots
    screen_image_filename = output_dir + "/screen_" + str(tid) + ".jpg"
    screen_image = pyautogui.screenshot(screen_image_filename, region = screen_region)

    minimap_image_filename = ""

    if include_minimap:
        minimap_image_filename = output_dir + "/minimap_" + str(tid) + ".jpg"
        minimap_image = pyautogui.screenshot(minimap_image_filename, region = minimap_region)

    if draw_axis:
        # draw axis on the screenshot
        draw = ImageDraw.Draw(screen_image)
        width, height = screen_image.size
        cx, cy = width // 2, height // 2

        draw.line((cx, 0, cx, height), fill="blue", width=3)  # Y
        draw.line((0, cy, width, cy), fill="blue", width=3)  # X

        font = ImageFont.truetype("arial.ttf", 30)
        offset_for_text = 30
        interval = 0.1
        for i in range(10):
            if i > 0:
                draw.text((cx + interval * (i ) * width // 2, cy), str(i ), fill="blue", font = font)
                draw.text((cx - interval * (i) * width // 2, cy), str(-i), fill="blue", font = font)
                draw.text((cx - offset_for_text - 10, cy + interval * (i ) * height // 2), str(-i), fill="blue", font = font)
            draw.text((cx - offset_for_text, cy - interval * (i ) * height // 2), str(i), fill="blue", font = font)

        axes_image_filename = output_dir + "/axes_screen_" + str(tid) + ".jpg"
        screen_image.save(axes_image_filename)

    return screen_image_filename, minimap_image_filename


def segment_minimap(screenshot_path):
    
    tid = time.time()
    output_dir = config.work_dir
    minimap_image_filename = output_dir + "/minimap_" + str(tid) + ".jpg"

    minimap_region = config.base_minimap_region
    minimap_region = [int(x * (config.game_resolution[0] / config.base_resolution[0]) ) for x in minimap_region] # (56, 725, 56 + 320, 725 + 320)
    minimap_region[2] += minimap_region[0]
    minimap_region[3] += minimap_region[1]

    # Open the source image file
    with Image.open(screenshot_path) as source_image:

        # Crop the image using the crop_rectangle
        cropped_minimap = source_image.crop(minimap_region)

        # Save the cropped image to a new file
        cropped_minimap.save(minimap_image_filename)

    return minimap_image_filename


def is_env_paused():

    is_paused = False
    confidence_threshold = 0.85

    # multiple-scale-template-matching example, decide whether the game is paused according to the confidence score
    pause_clock_template_file = './res/icons/clock.jpg'
    
    screenshot = take_screenshot(time.time(), include_minimap=False)[0]
    match_info = match_template_image(screenshot, pause_clock_template_file, debug=True, output_bb=True, save_matches=True, scale='full')

    is_paused = match_info[0]['confidence'] >= confidence_threshold

    return is_paused
