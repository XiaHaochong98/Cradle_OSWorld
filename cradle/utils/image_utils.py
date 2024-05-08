import os
import datetime
import io

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageChops, ImageFont, ImageEnhance
from scipy.ndimage import binary_fill_holes
import matplotlib.pyplot as plt

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


def draw_mouse_pointer(image: cv2.typing.MatLike, x, y):

    mouse_cursor = cv2.imread('./res/icons/pink_mouse.png', cv2.IMREAD_UNCHANGED)

    if mouse_cursor is None:
        logger.error("Failed to read mouse cursor image file.")
    elif x is None or y is None:
        logger.warn("Mouse coordinates are missing.")
    else:
        new_size = (mouse_cursor.shape[1] // 4, mouse_cursor.shape[0] // 4)
        mouse_cursor = cv2.resize(mouse_cursor, new_size, interpolation=cv2.INTER_AREA)
        image_array = image

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

            image = cv2.cvtColor(image_array, cv2.COLOR_BGRA2BGR)

    return image


def draw_mouse_pointer_file_(image_path: str, x, y) -> str:

    image = cv2.imread(image_path)
    image_with_mouse = draw_mouse_pointer(image, x, y)

    draw_mouse_img_path = image_path.replace(".jpg", f"_with_mouse.jpg")
    cv2.imwrite(draw_mouse_img_path, image_with_mouse)
    logger.debug(f"The image with mouse pointer is saved at {draw_mouse_img_path}")

    return draw_mouse_img_path


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


def resize_image(image: str | np.ndarray, resize_ratio) -> Image:
    """Resize the given image.

    Args:
        image (str | np.ndarray): The image to be resized.

    Returns:
        Image: The resized image.

    """
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    else:
        image = Image.open(image)
    new_size = [int(dim * resize_ratio) for dim in image.size]
    image_resized = image.resize(new_size)
    return image_resized


def overlay_image_on_background(annotations: list, shape) -> Image:
    if len(annotations) == 0:
        return

    img_data = np.ones((shape[0], shape[1], 4), dtype=np.uint8)

    sorted_anns = sorted(annotations, key=lambda x: x["area"], reverse=True)

    for ann in sorted_anns:
        m = ann["segmentation"]
        color_mask = np.concatenate([np.random.rand(3) * 255, [89]])
        img_data[m] = color_mask

    # Convert the NumPy array to a PIL Image and save
    img = Image.fromarray(img_data.astype('uint8'), 'RGBA')

    return img


def process_image_for_masks(original_image: Image) -> list[np.ndarray]:
    """
    Process the image to find unique masks based on color channels.

    Args:
    original_image: A Image object of the original image.

    Returns:
    A list of numpy.ndarrays, each representing a unique mask.
    """
    logger.debug("starting...")
    original_image_np = np.array(original_image)

    # Assume the last channel is the alpha channel if the image has 4 channels
    if original_image_np.shape[2] == 4:
        original_image_np = original_image_np[:, :, :3]

    # Find unique colors in the image, each unique color corresponds to a unique mask
    unique_colors = np.unique(original_image_np.reshape(-1, original_image_np.shape[2]), axis=0)
    logger.debug(f"{len(unique_colors)=}")

    masks = []
    for color in unique_colors:
        # Create a mask for each unique color
        mask = np.all(original_image_np == color, axis=-1)
        masks.append(mask)

    logger.debug(f"{len(masks)=}")
    return masks


def display_binary_images_grid(images: list[np.ndarray], grid_size = None, margin: int = 10, cell_size = None):
    """
    Display binary ndarrays as images on a grid with clear separation between grid cells,
    scaling images down as necessary.

    Args:
    images: A list of binary numpy.ndarrays.
    grid_size: Optional tuple (rows, cols) indicating the grid size.
               If not provided, a square grid size will be calculated.
    margin: The margin size between images in the grid.
    cell_size: Optional tuple (width, height) indicating the maximum size for any image cell in the grid.
               Images will be scaled down to fit within this size while maintaining aspect ratio.
    """
    if grid_size is None:
        grid_size = (int(np.ceil(np.sqrt(len(images)))),) * 2

    if cell_size is None:
        # Determine max dimensions of images in the list and use that as cell size
        cell_width = max(image.shape[1] for image in images) + margin
        cell_height = max(image.shape[0] for image in images) + margin
    else:
        cell_width, cell_height = cell_size

    # Create a new image with a white background
    total_width = cell_width * grid_size[1]
    total_height = cell_height * grid_size[0]
    grid_image = Image.new('1', (total_width, total_height), 1)

    for index, binary_image in enumerate(images):
        img = Image.fromarray(binary_image.astype(np.uint8) * 255, 'L').convert('1')

        # Scale down the image to fit within the cell size, maintaining aspect ratio
        img.thumbnail((cell_width - margin, cell_height - margin))

        # Create a new image with margins
        img_with_margin = Image.new('1', (img.width + margin, img.height + margin), 1)
        img_with_margin.paste(img, (margin // 2, margin // 2))

        # Calculate the position on the grid
        row, col = divmod(index, grid_size[1])
        x = col * cell_width
        y = row * cell_height

        # Paste the image into the grid
        grid_image.paste(img_with_margin, (x, y))

    # Display the grid image
    return grid_image


def remove_border_masks(masks: list[np.ndarray], threshold_percent: float = 5.0) -> list[np.ndarray]:
    """
    Removes masks whose "on" pixels are close to the mask borders on all four sides.

    Parameters:
    - masks: A list of ndarrays, where each ndarray is a binary mask.
    - threshold_percent: A float indicating how close the "on" pixels can be to the border,
                         represented as a percentage of the mask's dimensions.

    Returns:
    - A list of ndarrays with the border masks removed.
    """
    def is_close_to_all_borders(mask: np.ndarray, threshold: float) -> bool:
        # Determine actual threshold in pixels based on the percentage
        threshold_rows = int(mask.shape[0] * (threshold_percent / 100))
        threshold_cols = int(mask.shape[1] * (threshold_percent / 100))

        # Check for "on" pixels close to each border
        top = np.any(mask[:threshold_rows, :])
        bottom = np.any(mask[-threshold_rows:, :])
        left = np.any(mask[:, :threshold_cols])
        right = np.any(mask[:, -threshold_cols:])

        # If "on" pixels are close to all borders, return True
        return top and bottom and left and right

    logger.debug(f"{len(masks)=}")

    filtered_masks = []
    for mask in masks:
        # Only add mask if it is not close to all borders
        if not is_close_to_all_borders(mask, threshold_percent):
            filtered_masks.append(mask)

    logger.debug(f"{len(filtered_masks)=}")
    return filtered_masks


def filter_thin_ragged_masks(masks: list[np.ndarray], kernel_size: int = 3, iterations: int = 5) -> list[np.ndarray]:
    """
    Applies morphological operations to filter out thin and ragged masks.

    Parameters:
    - masks: A list of ndarrays, where each ndarray is a binary mask.
    - kernel_size: Size of the structuring element.
    - iterations: Number of times the operation is applied.

    Returns:
    - A list of ndarrays with thin and ragged masks filtered out.
    """
    logger.debug(f"{len(masks)=}")
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    filtered_masks = []

    for mask in masks:
        # Convert boolean mask to uint8
        try:
            mask_uint8 = mask.astype(np.uint8) * 255
        except MemoryError:
            logger.error("MemoryError: Mask is too large to convert to uint8.")
            continue
        # Perform erosion
        eroded_mask = cv2.erode(mask_uint8, kernel, iterations=iterations)
        # Perform dilation
        dilated_mask = cv2.dilate(eroded_mask, kernel, iterations=iterations)

        # Convert back to boolean mask and add to the filtered list
        filtered_masks.append(dilated_mask > 0)

    logger.debug(f"{len(filtered_masks)=}")
    return filtered_masks


def refine_masks(masks: list[np.ndarray]) -> list[np.ndarray]:
    """
    Refine the list of masks:
    - Fill holes of any size
    - Remove masks completely contained within other masks.

    Args:
        masks: A list of numpy.ndarrays, each representing a mask.

    Returns:
        A list of numpy.ndarrays, each representing a refined mask.
    """
    logger.debug(f"{len(masks)=}")

    masks = remove_border_masks(masks)
    masks = filter_thin_ragged_masks(masks)

    # Fill holes in each mask
    filled_masks = [binary_fill_holes(mask).astype(np.uint8) for mask in masks]

    # Remove masks completely contained within other masks
    refined_masks = []
    for i, mask_i in enumerate(filled_masks):
        contained = False
        for j, mask_j in enumerate(filled_masks):
            if i != j:
                # Check if mask_i is completely contained in mask_j
                if np.array_equal(mask_i & mask_j, mask_i):
                    contained = True
                    break
        if not contained:
            refined_masks.append(mask_i)

    logger.debug(f"{len(refined_masks)=}")
    return refined_masks


def extract_masked_images(original_image: Image, masks: list[np.ndarray]):
    """
    Apply each mask to the original image and resize the image to fit the mask's bounding box,
    discarding pixels outside the mask.

    Args:
    original_image: A Image object of the original image.
    masks: A list of numpy.ndarrays, each representing a refined mask.

    Returns:
    A list of Image objects, each cropped to the mask's bounding box and containing the content of the original image within that mask.
    """
    logger.debug(f"{len(masks)=}")
    original_image_np = np.array(original_image)
    masked_images = []

    for mask in masks:
        # Find the bounding box of the mask
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]

        # Crop the mask and the image to the bounding box
        cropped_mask = mask[rmin:rmax+1, cmin:cmax+1]
        cropped_image = original_image_np[rmin:rmax+1, cmin:cmax+1]

        # Apply the mask
        masked_image = np.where(cropped_mask[:, :, None], cropped_image, 0).astype(np.uint8)
        masked_images.append(Image.fromarray(masked_image))

    logger.debug(f"{len(masked_images)=}")
    return masked_images


def calculate_bounding_boxes(masks: list[np.ndarray]):
    """
    Calculate bounding boxes and centers for each mask in the list separately.

    Args:
        masks: A list of numpy.ndarrays, each representing a mask.

    Returns:
        A tuple containing two lists:
        - The first list contains dictionaries, each containing the "top", "left", "height", "width" of the bounding box for each mask.
        - The second list contains tuples, each representing the "center" as a tuple of (x, y) for each mask.
    """
    bounding_boxes = []
    centroids = []
    for mask in masks:
        # Find all indices where mask is True
        rows, cols = np.where(mask)
        if len(rows) == 0 or len(cols) == 0:  # In case of an empty mask
            bounding_boxes.append({})
            centroids.append((float('nan'), float('nan')))
            continue

        # Calculate bounding box
        top, left = rows.min(), cols.min()
        height, width = rows.max() - top, cols.max() - left

        # Calculate center
        center_x, center_y = left + width / 2, top + height / 2

        # Append data to the lists
        bounding_boxes.append({
            "top": float(top),
            "left": float(left),
            "height": float(height),
            "width": float(width),
        })
        centroids.append((float(center_x), float(center_y)))

    return bounding_boxes, centroids


def plot_som(screenshot_filename, bounding_boxes):
    org_img = Image.open(screenshot_filename)
    draw = ImageDraw.Draw(org_img)
    font_path = "arial.ttf"
    font_size, padding = 16, 2
    font = ImageFont.truetype(font_path, font_size)

    # Create a color cycle using one of the categorical color palettes in matplotlib
    color_cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    text_to_draw = []
    min_distance_from_edge = 30

    # Draw each bounding box on the image
    for i, bbox in enumerate(bounding_boxes):
        if len(bbox) == 0:
            continue
        # Calculate the bottom-right corner of the bounding box
        top, right, bottom, left = (
            bbox['top'],
            bbox['left'] + bbox['width'],
            bbox['top'] + bbox['height'],
            bbox['left'],
        )

        bbox_padding = 0
        bbox_border = 2
        color = color_cycle[i % len(color_cycle)]
        draw.rectangle(
            [
                left - bbox_padding,
                top - bbox_padding,
                right + bbox_padding,
                bottom + bbox_padding,
            ],
            outline=color,
            width=bbox_border,
        )

        # Calculate list of possible text positions
        text_positions = [
            (left - font_size, top - font_size),  # Default top-left corner
            (right - font_size - 2 * padding, bottom)  # Bottom-right corner
        ]
        unique_id = str(i + 1)
        text_width = draw.textlength(unique_id, font=font)
        text_height = font_size

        # Check if the default top-left position is too close to the top or left
        if left < min_distance_from_edge or top < min_distance_from_edge:
            # If too close to the left or top, use bottom-right corner
            text_position = (
                text_positions[1][0] + padding,
                text_positions[1][1],
            )
        else:
            # Otherwise, use top-left corner
            text_position = (
                text_positions[0][0] + padding,
                text_positions[0][1],
            )

        new_text_rectangle = [
            text_position[0] - padding,
            text_position[1] - padding,
            text_position[0] + text_width + padding,
            text_position[1] + text_height + padding,
        ]

        text_to_draw.append(
            (new_text_rectangle, text_position, unique_id, color)
        )

        for text_rectangle, text_position, unique_id, color in text_to_draw:
            # Draw a background rectangle for the text
            draw.rectangle(text_rectangle, fill=color)
            draw.text(text_position, unique_id, font=font, fill="white")

    return org_img


def enhance_contrast(image: Image, contrast_level: float) -> Image:
    enhancer = ImageEnhance.Contrast(image)
    contrasted_image = enhancer.enhance(contrast_level)
    return contrasted_image


def crop_grow_image(image_path: str, crop_area_border: tuple[int, int, int, int] = (8, 1, 8, 8), overwrite_flag: bool = False):
    with Image.open(image_path) as img:
        width, height = img.size
        crop_area = (crop_area_border[0], crop_area_border[1], width-crop_area_border[2], height-crop_area_border[3])
        cropped_img = img.crop(crop_area)
        cropped_img = cropped_img.resize(config.DEFAULT_ENV_RESOLUTION, Image.ANTIALIAS)
        if overwrite_flag:
            crop_screenshot_path = image_path
        else:
            crop_screenshot_path = image_path.replace(".jpg", f"_crop.jpg")
        cropped_img.save(crop_screenshot_path)
        return crop_screenshot_path
