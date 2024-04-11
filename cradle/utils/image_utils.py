import os
from datetime import datetime

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageChops

from cradle.config import Config
from cradle.gameio import IOEnvironment
from cradle.log import Logger

config = Config()
io_env = IOEnvironment()
logger = Logger()


def show_image(img):
    if isinstance(img, str):
        img = cv2.imread(img)
    cv2.namedWindow("display", cv2.WINDOW_NORMAL)
    cv2.imshow("display", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def minimap_movement_detection(image_path1, image_path2, threshold = 30):
    '''
    Detect whether two minimaps are the same to determine whether the character moves successfully.
    Args:
        image_path1, image_path2: 2 minimap images to be detected.
        threshold: pixel-level threshold for minimap movement detection, default 30.

    Returns:
        change_detected: True if the movements is above the threshold,
        img_matches: Draws the found matches of keypoints from two images. Can be visualized by plt.imshow(img_matches)
    '''
    img1 = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)

    orb = cv2.ORB_create()
    keypoints1, descriptors1 = orb.detectAndCompute(img1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(img2, None)

    if type(descriptors1) != type(None) and type(descriptors2) != type(None):
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(descriptors1, descriptors2)
    else:
        return True, None, None

    matches = sorted(matches, key = lambda x:x.distance)

    img_matches = cv2.drawMatches(img1, keypoints1, img2, keypoints2, matches[:20], None, flags=2)
    best_matches = matches[:20]

    average_distance = np.mean([m.distance for m in best_matches])

    change_detected = average_distance > (threshold * config.resolution_ratio) or np.allclose(average_distance, 0, atol=1e-3)
    return change_detected, img_matches, average_distance


def _draw_rectangle(draw, coords, outline="red", width=50):
    x1, y1, x2, y2 = coords
    draw.line([x1, y1, x2, y1], fill=outline, width=width)
    draw.line([x1, y2, x2, y2], fill=outline, width=width)
    draw.line([x1, y1, x1, y2], fill=outline, width=width)
    draw.line([x2, y1, x2, y2], fill=outline, width=width)


def draw_region_on_image(image_path, coordinates, pic_name):

    coords = eval(coordinates)

    image = Image.open(image_path)
    canvas = ImageDraw.Draw(image)
    width, height = image.size

    if len(coords) == 2:
        x, y = coords[0] * width, coords[1] * height
        _draw_rectangle(canvas, [x-1, y-1, x+1, y+1])
    elif len(coords) == 4:
        x1, y1, x2, y2 = coords[0] * width, coords[1] * height, coords[2] * width, coords[3] * height
        _draw_rectangle(canvas, [x1, y1, x2, y2], width=5)
    else:
        msg = "Coordinates must be two- or four-digit tuples"
        logger.error(msg)
        raise ValueError(msg)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Store image where the original image is, add the pic_name and time to the new image name
    tokens = image_path.rsplit('.', 1)
    base_path_to_filename = tokens[0]
    file_extension = tokens[1]

    output_path = f'{base_path_to_filename}_{pic_name}_{timestamp}.{file_extension}'
    image.save(output_path)
    logger.debug(f"Picture saved: {output_path}")


def draw_mouse_pointer(image):

    mouse_cursor = cv2.imread('./res/icons/pink_mouse.png', cv2.IMREAD_UNCHANGED)

    if mouse_cursor is None:
        logger.error("Failed to read mouse cursor image file.")
    else:
        new_size = (mouse_cursor.shape[1] // 4, mouse_cursor.shape[0] // 4)
        mouse_cursor = cv2.resize(mouse_cursor, new_size, interpolation=cv2.INTER_AREA)
        x, y = io_env.get_mouse_position()
        image_array = np.array(image)

        if x + mouse_cursor.shape[1] > 0 and y + mouse_cursor.shape[0] > 0 and x < image_array.shape[1] and y < image_array.shape[0]:
            x_start = max(x, 0)
            y_start = max(y, 0)
            x_end = min(x + mouse_cursor.shape[1], image_array.shape[1])
            y_end = min(y + mouse_cursor.shape[0], image_array.shape[0])
            mouse_cursor_part = mouse_cursor[max(0, -y):y_end-y, max(0, -x):x_end-x]

            for c in range(3):
                alpha_channel = mouse_cursor_part[:, :, 3] / 255.0
                image_array[y_start:y_end, x_start:x_end, c] = \
                    alpha_channel * mouse_cursor_part[:, :, c] + \
                    (1 - alpha_channel) * image_array[y_start:y_end, x_start:x_end, c]

            image = Image.fromarray(image_array)

    return image


def calculate_image_diff(path_1, path_2):

    if not os.path.exists(path_1):
        logger.error(f"The file at {path_1} does not exist.")
        raise FileNotFoundError(f"The file at {path_1} does not exist.")

    if not os.path.exists(path_2):
        logger.error(f"The file at {path_2} does not exist.")
        raise FileNotFoundError(f"The file at {path_2} does not exist.")

    img1 = Image.open(path_1)
    img2 = Image.open(path_2)

    if img1.size != img2.size:
        msg = "Images do not have the same size."
        logger.error(msg)
        raise ValueError(msg)

    diff = ImageChops.difference(img1, img2)
    diff = diff.convert("RGBA")

    pixels = diff.load()
    width, height = diff.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if r == g == b == 0:
                pixels[x, y] = (0, 0, 0, 0)
            else:
                pixels[x, y] = (r, g, b, 255)

    return diff


def save_image_diff(path_1, path_2):
    diff = calculate_image_diff(path_1, path_2)

    img1_name = os.path.splitext(os.path.basename(path_1))[0]
    img2_name = os.path.splitext(os.path.basename(path_2))[0]

    output_filename = f"diff_{img1_name}_{img2_name}.png"
    output_path = os.path.join(os.path.dirname(path_1), output_filename)
    diff.save(output_path)
    logger.debug(f"Picture saved: {output_path}")

    return output_path


def calculate_pixel_diff(output_path):
    img = Image.open(output_path).convert("RGBA")
    pixels = img.load()
    width, height = img.size

    non_transparent_count = 0
    for y in range(height):
        for x in range(width):
            _, _, _, a = pixels[x, y]
            if a != 0:
                non_transparent_count += 1

    return non_transparent_count
