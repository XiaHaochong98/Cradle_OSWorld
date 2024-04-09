import time
from typing import Any

from PIL import Image, ImageDraw, ImageFont
import mss
import mss.tools
import cv2
import numpy as np
import mss
import mss.tools

from cradle.config import Config
from cradle.log import Logger
from cradle.gameio import IOEnvironment

config = Config()
logger = Logger()
io_env = IOEnvironment()


def switch_to_game():
    target_window = io_env.get_windows_by_name(config.env_name)[0]
    try:
        target_window.activate()
    except Exception as e:
        if "Error code from Windows: 0" in str(e):
            # Handle pygetwindow exception
            pass
        else:
            raise e

    time.sleep(1)


def take_screenshot(tid : float,
                    screen_region : tuple[int, int, int, int] = None,
                    minimap_region : tuple[int, int, int, int] = None,
                    include_minimap = False,
                    draw_axis = False,
                    show_mouse_in_screenshot = config.show_mouse_in_screenshot):

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

        if show_mouse_in_screenshot:
            mouse_cursor = cv2.imread('./res/icons/pink_mouse.png', cv2.IMREAD_UNCHANGED)
            if mouse_cursor is None:
                logger.error("Failed to read mouse cursor image file.")
            else:
                new_size = (mouse_cursor.shape[1] // 4, mouse_cursor.shape[0] // 4)
                mouse_cursor = cv2.resize(mouse_cursor, new_size, interpolation=cv2.INTER_AREA)
                x, y = io_env.get_mouse_position()
                x = max(region['left'], min(x, region['left'] + region['width'] - mouse_cursor.shape[1]))
                y = max(region['top'], min(y, region['top'] + region['height'] - mouse_cursor.shape[0]))
                image_array = np.array(image)

                for c in range(0, 3):
                    image_array[y:y + mouse_cursor.shape[0], x:x + mouse_cursor.shape[1], c] = \
                        mouse_cursor[:, :, c] * (mouse_cursor[:, :, 3] / 255.0) + \
                        image_array[y:y + mouse_cursor.shape[0], x:x + mouse_cursor.shape[1], c] * \
                        (1.0 - mouse_cursor[:, :, 3] / 255.0)

                image = Image.fromarray(image_array)

        image.save(screen_image_filename)

    minimap_image_filename = ""

    if include_minimap:
        minimap_image_filename = output_dir + "/minimap_" + str(tid) + ".jpg"

        mm_region = minimap_region
        mm_region = {
            "left": mm_region[0],
            "top": mm_region[1],
            "width": mm_region[2],
            "height": mm_region[3],
        }

        with mss.mss() as sct:
            minimap_image = sct.grab(mm_region)
            mm_image = Image.frombytes("RGB", minimap_image.size, minimap_image.bgra, "raw", "BGRX")
            mm_image.save(minimap_image_filename)

        clip_minimap(minimap_image_filename)

    if draw_axis:
        # Draw axis on the screenshot
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


def clip_minimap(minimap_image_filename):

    image = cv2.imread(minimap_image_filename)

    # Get the dimensions of the image
    height, width = image.shape[:2]

    # Create a mask of the same size as the image, initialized to white
    mask = np.ones((height, width, 3), dtype=np.uint8) * 255

    # Define the size of the triangular mask at each corner
    triangle_size = int(180 * config.resolution_ratio)

    # Draw black triangles on the four corners of the mask
    # Top-left corner
    cv2.fillConvexPoly(mask, np.array([[0, 0], [triangle_size, 0], [0, triangle_size]]), 0)

    # Top-right corner
    cv2.fillConvexPoly(mask, np.array([[width, 0], [width - triangle_size, 0], [width, triangle_size]]), 0)

    # Bottom-left corner
    cv2.fillConvexPoly(mask, np.array([[0, height], [0, height - triangle_size], [triangle_size, height]]), 0)

    # Bottom-right corner
    cv2.fillConvexPoly(mask, np.array([[width, height], [width, height - triangle_size], [width - triangle_size, height]]), 0)

    # Apply the mask to the image
    masked_image = cv2.bitwise_and(image, mask)

    # Save the result
    cv2.imwrite(minimap_image_filename, masked_image)


__all__ = [
    "switch_to_game",
    "take_screenshot",
    "clip_minimap"
]
