import numpy as np
from segment_anything import (
    SamAutomaticMaskGenerator,
    SamPredictor,
    sam_model_registry,
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
    enhance_contrast
)

config = Config()
logger = Logger()


class SamProvider(metaclass=Singleton):

    def __init__(self):

        self.sam_model = None
        self.sam_predictor = None
        self.sam_mask_generator = None

        # try:
        self.sam_model = sam_model_registry[config.sam_model_name](checkpoint="./cache/sam_vit_h_4b8939.pth").to("cuda")
        self.sam_predictor = SamPredictor(self.sam_model)
        self.sam_mask_generator = SamAutomaticMaskGenerator(self.sam_model, pred_iou_thresh=config.sam_pred_iou_thresh)
    # except Exception as e:
        #     logger.error(f"Failed to load the SAM model. Make sure you follow the instructions on README to download the necessary files.\n{e}")


    def get_som(self, screenshot_path):
        mask_img = None
        refined_masks = []

        image_resized = resize_image(screenshot_path, resize_ratio=config.sam_resize_ratio)
        contrasted_image = enhance_contrast(image_resized, config.sam_contrast_level)
        array = np.array(contrasted_image)
        original_masks = self.sam_mask_generator.generate(array)
        total_area = array.shape[0] * array.shape[1]
        del image_resized
        del contrasted_image

        # Process each mask and check area if it is larger than the threshold. If so, process it again with SAM.
        for i, mask in enumerate(original_masks):
            mask_area = np.sum(mask['segmentation'])
            if mask_area / total_area > config.sam_max_area:
                # Process this large area with SAM again
                large_mask_img = overlay_image_on_background([mask], array.shape)  
                refined_large_mask = process_image_for_masks(large_mask_img)[0]  

                # Create a dictionary for the large mask to maintain consistency with the expected format
                refined_large_mask_dict = {'segmentation': refined_large_mask, 'area': np.sum(refined_large_mask)}
                refined_masks.append(refined_large_mask_dict)
                del large_mask_img
                del refined_large_mask
                
            else:
                refined_masks.append(mask)  # Append the original mask

        mask_img = overlay_image_on_background(refined_masks, array.shape)
        refined_masks = [mask['segmentation'] for mask in refined_masks]
        del array
        masks = process_image_for_masks(mask_img)
        del mask_img

        resized_masks = []
        # Resize the masks to the original size
        for mask in masks:
            try:
                mask_uint8 = mask.astype(np.uint8) * 255
                resized_mask = np.array(resize_image(mask_uint8, resize_ratio=1 / config.sam_resize_ratio))
                resized_masks.append(resized_mask)
            except MemoryError:
                logger.error("MemoryError: Mask is too large to convert to uint8.")
                continue 

        refined_masks = refine_masks(resized_masks)
        bounding_boxes, centroids = calculate_bounding_boxes(refined_masks)

        som_img = plot_som(screenshot_path, bounding_boxes)
        centroids_map = {str(i + 1): centroid for i, centroid in enumerate(centroids)}
        del resized_masks 

        return som_img, centroids_map
    
    
    def load_som_results(self, screenshot_path):
        som_img_path = screenshot_path.replace(".jpg", f"_som.jpg")
        som_img, centroids_map = self.get_som(screenshot_path)
        som_img.save(som_img_path)
        logger.debug(f"Saved the SOM screenshot to {som_img_path}")
        return som_img_path, centroids_map
