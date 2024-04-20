import numpy as np
from segment_anything import (
    SamAutomaticMaskGenerator,
    SamPredictor,
    sam_model_registry,
    enhance_contrast,
)

from cradle.utils import Singleton
from cradle.config import Config
from cradle.log import Logger
from cradle.utils.image_utils import (
    resize_image,
    overlay_image_on_background,
    process_image_for_masks,
    refine_masks,
    calculate_bounding_boxes,
    plot_som,
)

config = Config()
logger = Logger()


class SamProvider(metaclass=Singleton):

    def __init__(self):

        self.sam_model = None
        self.sam_predictor = None
        self.sam_mask_generator = None

        try:
            self.sam_model = sam_model_registry[config.sam_model_name](checkpoint="./cache/sam_vit_h_4b8939.pth").to("cuda")
            self.sam_predictor = SamPredictor(self.sam_model)
            self.sam_mask_generator = SamAutomaticMaskGenerator(self.sam_model, pred_iou_thresh=config.sam_pred_iou_thresh)
        except Exception as e:
            logger.error(f"Failed to load the grounding model. Make sure you follow the instructions on README to download the necessary files.\n{e}")


    def get_som(self, screenshot_path):
        image_resized = resize_image(screenshot_path, resize_ratio=config.sam_resize_ratio)
        contrasted_image = enhance_contrast(image_resized, config.sam_contrast_level)
        array = np.array(contrasted_image)
        masks = self.sam_mask_generator.generate(array)
        bbox_list = []
        for mask in masks:
            bbox_list.append(mask["bbox"])

        mask_img = overlay_image_on_background(masks, array.shape)
        masks = process_image_for_masks(mask_img)
        masks = [np.array(resize_image(mask.astype(np.uint8) * 255, resize_ratio=1 / config.sam_resize_ratio)) for mask in masks]
        refined_masks = refine_masks(masks)
        bounding_boxes, centroids = calculate_bounding_boxes(refined_masks)

        som_img = plot_som(screenshot_path, bounding_boxes)
        som_screenshot_path = screenshot_path.replace(".jpg", f"_som.jpg")
        som_img.save(som_screenshot_path)

        centroids_map = {str(i + 1): centroid for i, centroid in enumerate(centroids)}

        return som_screenshot_path, centroids_map
