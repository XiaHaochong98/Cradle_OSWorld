import shutil, os
import time, math

import cv2
import torch
from torchvision.ops import box_convert
from groundingdino.util.inference import load_model, load_image, predict, annotate

from uac.gameio.atomic_skills.hunt import shoot
from uac.gameio.lifecycle.ui_control import switch_to_game, take_screenshot
from uac.gameio.skill_registry import register_skill
from uac.provider import GdProvider
from uac.config import Config
from uac.log import Logger

config = Config()
logger = Logger()
gd_detector = GdProvider()


@register_skill("shoot_people")
def shoot_people():
    """
    Shoot at person-shaped targets, if necessary.
    """
    keep_shooting_target(500, detect_target="person", debug=False)


@register_skill("shoot_wolves")
def shoot_wolves():
    """
    Shoot at wolf targets, if necessary.
    """
    keep_shooting_target(500, detect_target="wolf", debug=False)


def keep_shooting_target(
        iterations,
        detect_target="wolf",
        debug=True
):
    '''
    Keep shooting the 'detect_target' detected by object detector automatically.
    '''
    save_dir = config.work_dir

    for step in range(iterations):
        if debug:
            logger.debug(f'Go for hunting #{step}')

        timestep = time.time()

        screen_image_filename, minimap_image_filename = take_screenshot(timestep, config.game_region,
                                                                        config.minimap_region, draw_axis=False)
        if not detect_target.endswith(' .'):
            detect_target += ' .'

        screen, boxes, logits, phrases = gd_detector.detect(screen_image_filename, detect_target, box_threshold=0.4)

        if "Person" in detect_target:
            if len(boxes) > 1:
                index = 0
                dis = 1.5
                for i in range(len(boxes)):
                    down_mid = (boxes[i, 0], boxes[i, 1] + boxes[i, 3] / 2)
                    distance = torch.sum(torch.abs(torch.tensor(down_mid) - torch.tensor((0.5, 1.0))))
                    if distance < dis:
                        dis = distance
                        index = i
                boxes = torch.cat([boxes[:index], boxes[index + 1:]])
                logits = torch.cat([logits[:index], logits[index + 1:]])
                phrases.pop(index)
                logger.debug(f'dis:{dis}  remove{index}')

            elif len(boxes) == 1:
                boxes = torch.tensor(boxes[1:])
                logits = torch.tensor(logits[1:])
                phrases.pop(0)

        if debug:
            annotated_frame = annotate(image_source=screen, boxes=boxes, logits=logits, phrases=phrases)
            cv2.imwrite(os.path.join(save_dir, f"annotated_{timestep}.jpg"), annotated_frame)
        h, w, _ = screen.shape
        xyxy = box_convert(boxes=boxes * torch.Tensor([w, h, w, h]), in_fmt="cxcywh", out_fmt="xyxy").numpy().astype(int)

        for detect_xyxy, detect_object, detect_confidence in zip(xyxy, phrases, logits):
            if debug:
                logger.debug(
                    f'detect_xyxy is {detect_xyxy},detect_object is {detect_object},shoot_xy is {int((detect_xyxy[0] + detect_xyxy[2]) / 2) - config.game_resolution[0] // 2},{int((detect_xyxy[1] + detect_xyxy[3]) / 2) - config.game_resolution[1] // 2}')

            if detect_object in detect_target:  # TODO: shoot confidence threshold
                shoot_x = int((detect_xyxy[0] + detect_xyxy[2]) / 2 - config.game_resolution[0] // 2)
                shoot_y = int((detect_xyxy[1] + detect_xyxy[3]) / 2 - config.game_resolution[1] // 2)
                if debug:
                    cv2.arrowedLine(annotated_frame, (config.game_resolution[0] // 2, config.game_resolution[1] // 2), (
                        int((detect_xyxy[0] + detect_xyxy[2]) / 2), int((detect_xyxy[1] + detect_xyxy[3]) / 2)),
                                    (0, 255, 0), 2, tipLength=0.1)
                    cv2.imwrite(os.path.join(save_dir, f"annotated_{detect_object}_{timestep}.jpg"), annotated_frame)
                logger.debug(f'pixel is {shoot_x},{shoot_y}')
                shoot(int(shoot_x), int(shoot_y))
                break

__all__ = [
    "shoot_people",
    "shoot_wolves"
]


