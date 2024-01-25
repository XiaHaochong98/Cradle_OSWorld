import os, math
import time

import pydirectinput
import pyautogui
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import torch
from torchvision.ops import box_convert
import supervision as sv
import mss
import mss.tools

from uac.config import Config
from uac.log import Logger
from uac.gameio import IOEnvironment
from uac.utils.template_matching import match_template_image

config = Config()
logger = Logger()
io_env = IOEnvironment()

PAUSE_SCREEN_WAIT = 1


def pause_game():

    # if io_env.check_held_keys():
    #    logger.warn("Not pausing because tab or B are held.")
    #    return

    if not is_env_paused():
        pydirectinput.press('esc')
    else:
        logger.debug("The environment is already paused!")

    # While game is paused, quickly re-center mouse location on x axis to avoid clipping at game window border with time
    io_env.ahk.mouse_move(config.game_resolution[0] // 2, config.game_resolution[1] // 2, speed=1, relative=False)

    io_env.handle_hold_in_pause()

    time.sleep(PAUSE_SCREEN_WAIT)


def unpause_game():
    if is_env_paused():
        pydirectinput.press('esc')
    else:
        logger.debug("The environment is not paused!")
    time.sleep(PAUSE_SCREEN_WAIT)

    io_env.handle_hold_in_unpause()


def exit_back_to_pause():

    max_steps = 10

    back_steps = 0
    while not is_env_paused() and back_steps < max_steps:
        back_steps += 1
        pydirectinput.press('esc')
        time.sleep(PAUSE_SCREEN_WAIT)

    if back_steps >= max_steps:
        logger.warn("The environment fails to pause!")


def exit_back_to_game():

    exit_back_to_pause()

    # Unpause the game, to keep the rest of the agent flow consistent
    unpause_game()


def switch_to_game():
    named_windows = pyautogui.getWindowsWithTitle(config.env_name)
    if len(named_windows) == 0:
        logger.error(f"Cannot find the game window {config.env_name}!")
        return
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


def switch_to_code():
    pause_game()
    pyautogui.hotkey("ctrl", "win", "right") # switch desktop


def take_screenshot(tid : float = 0.0,
                    screen_region : tuple[int, int, int, int] = config.game_region,
                    minimap_region : tuple[int, int, int, int] = config.minimap_region,
                    include_minimap = True,
                    draw_axis = False):

    region = screen_region
    region = {
        "left": region[0],
        "top": region[1],
        "width": region[2],
        "height": region[3],
    }

    output_dir = config.work_dir

    # save screenshots
    screen_image_filename = output_dir + "/screen_" + str(tid) + ".jpg"

    with mss.mss() as sct:
        screen_image = sct.grab(region)
        image = Image.frombytes("RGB", screen_image.size, screen_image.bgra, "raw", "BGRX")
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

    clip_minimap(minimap_image_filename)

    return minimap_image_filename


def is_env_paused():

    is_paused = False
    confidence_threshold = 0.85

    # Multiple-scale-template-matching example, decide whether the game is paused according to the confidence score
    pause_clock_template_file = './res/icons/clock.jpg'

    screenshot = take_screenshot(time.time(), include_minimap=False)[0]
    match_info = match_template_image(screenshot, pause_clock_template_file, debug=True, output_bb=True, save_matches=True, scale='full')

    is_paused = match_info[0]['confidence'] >= confidence_threshold

    # Renaming pause candidate screenshot to ease debugging or gameplay scenarios
    os.rename(screenshot, screenshot.replace('screen', 'pause_screen_candidate'))

    return is_paused


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


def annotate_with_coordinates(image_source, boxes, logits, phrases):
    h, w, _ = image_source.shape
    boxes = boxes * torch.Tensor([w, h, w, h])
    xyxy = box_convert(boxes=boxes, in_fmt="cxcywh", out_fmt="xyxy").numpy()
    logger.debug(f"boxes: {boxes}, xyxy: {xyxy}")

    detections = sv.Detections(xyxy=xyxy)

    # Without coordinates normalization
    labels = [
        f"{phrase} {' '.join(map(str, ['x=', round((xyxy_s[0]+xyxy_s[2])/(2*w), 2), 'y=', round((xyxy_s[1]+xyxy_s[3])/(2*h), 2)]))}"
        for phrase, xyxy_s
        in zip(phrases, xyxy)
    ]

    # Without coordinates normalization
    # labels = [
    #     f"{phrase} {' '.join(map(str, ['x=', round((xyxy_s[0]+xyxy_s[2])/2), 'y=', round((xyxy_s[1]+xyxy_s[3])/2)]))}"
    #     for phrase, xyxy_s
    #     in zip(phrases, xyxy)
    # ]

    box_annotator = sv.BoxAnnotator()
    annotated_frame = cv2.cvtColor(image_source, cv2.COLOR_RGB2BGR)
    annotated_frame = box_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)
    return annotated_frame


class CircleDetector:
    def __init__(self,resolution_ratio):
        if resolution_ratio <= .67:  # need super resolution
            self.sr_model = cv2.dnn_superres.DnnSuperResImpl_create()
            self.k = 2 if resolution_ratio <=.5 else 3
            self.sr_model.readModel(f'./res/models/ESPCN_x{self.k}.pb')
            self.sr_model.setModel('espcn', self.k)
        else:
            self.sr_model = None


    def get_theta(self, origin_x, origin_y, center_x, center_y):
        '''
        The origin of the image coordinate system is usually located in the upper left corner of the image, with the x-axis to the right indicating a positive direction and the y-axis to the down indicating a positive direction. Using vertical upward as the reference line, i.e. the angle between it and the negative direction of the y-axis
        '''
        theta = math.atan2(center_x - origin_x, origin_y - center_y)
        theta = math.degrees(theta)
        return theta


    def detect(self, img_file,
        yellow_range=np.array([[140, 230, 230], [170, 255, 255]]),
        gray_range=np.array([[165, 165, 165], [175, 175, 175]]),
        red_range=np.array([[0, 0, 170], [30, 30, 240]]),
        detect_mode='yellow & gray',
        debug=False
    ): 

        image = cv2.imread(img_file)

        # super resolution according to resolution ratio
        if self.sr_model is not None:
            image = self.sr_model.upsample(image)
            if self.k == 3:
                image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)

        origin = (image.shape[0] // 2, image.shape[1] // 2)
        circles = cv2.HoughCircles(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), cv2.HOUGH_GRADIENT, 1, 10, param1=200,param2=10, minRadius=5 * 2, maxRadius=8 * 2)
        theta = 0x3f3f3f3f
        measure = {'theta': theta, 'distance': theta, 'color': np.array([0, 0, 0]), 'confidence': 0, 'vis': image,
                   'center': origin}

        circles_info = []
        if circles is not None:

            circles = np.round(circles[0, :]).astype("int")

            for (x, y, r) in circles:
                # Crop the circle from the original image
                circle_img = np.zeros_like(image)
                cv2.circle(circle_img, (x, y), r, (255, 255, 255), thickness=-1)
                circle = cv2.bitwise_and(image, circle_img)

                # Define range for red color and create a mask
                red_mask = cv2.inRange(circle, red_range[0], red_range[1])
                gray_mask = cv2.inRange(circle, gray_range[0], gray_range[1])
                yellow_mask = cv2.inRange(circle, yellow_range[0], yellow_range[1])

                # Count red pixels in the circle
                red_count = cv2.countNonZero(red_mask)
                gray_count = cv2.countNonZero(gray_mask)
                yellow_count = cv2.countNonZero(yellow_mask)

                # Add circle information and color counts to the list
                circles_info.append({
                    "center": (x, y),
                    "radius": r,
                    "red_count": red_count,
                    "gray_count": gray_count,
                    "yellow_count": yellow_count
                })

            # Sort the circles based on yellow_count, gray_count, and red_count
            if 'red' in detect_mode:
                circles_info.sort(key=lambda c: (c['red_count'], c['yellow_count'], c['gray_count']), reverse=True)
                detect_criterion = lambda circle: circle["red_count"] >= 5
            else:
                circles_info.sort(key=lambda c: (c['yellow_count'], c['gray_count'], c['red_count']), reverse=True)
                detect_criterion = lambda circle: circle["gray_count"] >= 5 or circle["yellow_count"] >= 5

            for circle in circles_info:
                center_x, center_y, radius = circle["center"][0], circle["center"][1], circle["radius"]
                if detect_criterion(circle):
                    theta = self.get_theta(*origin, center_x, center_y)
                    dis = np.sqrt((center_x - origin[0]) ** 2 + (center_y - origin[1]) ** 2)
                    measure = {'theta': theta, 'distance': dis,
                               'color': "yellow" if circle["yellow_count"] >= 5 else "gray", 'confidence': 1,
                               'center': (center_x, center_y),
                               'bounding_box': (center_x - radius, center_y - radius, 2 * radius, 2 * radius)}
                    break

            if debug:
                for i, circle in enumerate(circles_info):
                    cv2.circle(image, circle["center"], circle["radius"], (0, 255, 0), 2)
                    cv2.putText(image, str(i + 1), (circle["center"][0] - 5, circle["center"][1] + 4),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                measure['vis'] = image

        return theta, measure
