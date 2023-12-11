import shutil, os
import time, math

import cv2
import torch
from torchvision.ops import box_convert

from uac.config import Config
from uac.log import Logger
from uac.gameio.skill_registry import register_skill
from uac.utils.file_utils import assemble_project_path
from uac.gameio.atomic_skills.move import turn, move_forward
from uac.gameio.atomic_skills.hunt import shoot, call_animals, reload_gun
from uac.gameio.composite_skills.go_to_icon import match_template, get_theta
from groundingdino.util.inference import load_model, load_image, predict, annotate
from uac.gameio.lifecycle.ui_control import switch_to_code, switch_to_game, take_screenshot, pause_game, unpause_game

config = Config()
logger = Logger()

model = load_model("./cache/GroundingDINO_SwinT_OGC.py",
                   "./cache/groundingdino_swint_ogc.pth")


def groundingDINO_detect(IMAGE_PATH,TEXT_PROMPT = "wolf .",BOX_TRESHOLD = 0.35,TEXT_TRESHOLD = 0.25,device='cuda'):

    image_source, image = load_image(IMAGE_PATH)
    b = time.time()

    boxes, logits, phrases = predict(
        model=model,
        image=image,
        caption=TEXT_PROMPT,
        box_threshold=BOX_TRESHOLD,
        text_threshold=TEXT_TRESHOLD,
        device=device
    )

    logger.write(f'{IMAGE_PATH} | device: {device} | time cost: {time.time()-b:.4f} s')
    
    annotated_frame = annotate(image_source=image_source, boxes=boxes, logits=logits, phrases=phrases)
    cv2.imwrite(os.path.join(config.work_dir, "annotated_image.jpg"), annotated_frame)

    logger.write()

def shooting(
        total_steps,
        follow_dis_threshold,
        shoot_template_file=None,
        debug=True
):
    save_dir = config.work_dir
    follow_dis_threshold *= config.resolution_ratio

    # logger.write(f'{os.environ.get("TRANSFORMERS_OFFLINE", "A")}')
    # logger.write(f'{os.environ.get("HUGGINGFACE_HUB_CACHE", "B")}')

    TEXT_PROMPT = "wolf ."#"horse . person . wolf ."
    BOX_TRESHOLD = 0.5
    TEXT_TRESHOLD = 0.25
    shoot_dis_threshold = 40

    switch_to_game()
    call_animals()

    for step in range(total_steps):
        logger.write(f'Go for hunting #{step}')
        timestep = time.time()

        screen_image_filename, minimap_image_filename = take_screenshot(timestep, config.game_region,
                                                                        config.minimap_region, draw_axis=False)

        screen, screen_transformed = load_image(os.path.join(save_dir, f"screen_{timestep}.jpg"))
        boxes, logits, phrases = predict(
            model=model,
            image=screen_transformed,
            caption=TEXT_PROMPT,
            box_threshold=BOX_TRESHOLD,
            text_threshold=TEXT_TRESHOLD,
            device='cuda'
        )
    
        if debug:
            annotated_frame = annotate(image_source=screen, boxes=boxes, logits=logits, phrases=phrases)
            cv2.imwrite(os.path.join(save_dir, f"annotated_{timestep}.jpg"), annotated_frame)
        h, w, _ = screen.shape
        xyxy = box_convert(boxes=boxes * torch.Tensor([w, h, w, h]), in_fmt="cxcywh", out_fmt="xyxy").numpy().astype(
            int)
    
        for detect_xyxy, detect_object, detect_confidence in zip(xyxy, phrases, logits):
            if debug:
                logger.debug(
                    f'detect_xyxy is {detect_xyxy},detect_object is {detect_object},shoot_xy is {int((detect_xyxy[0] + detect_xyxy[2]) / 2) - config.game_resolution[0] // 2},{int((detect_xyxy[1] + detect_xyxy[3]) / 2) - config.game_resolution[1] // 2}')
    
            if 'wolf' == detect_object:  # TODO: shoot confidence threshold
                shoot_x = int((detect_xyxy[0] + detect_xyxy[2]) / 2 - config.game_resolution[0] // 2)
                shoot_y = int((detect_xyxy[1] + detect_xyxy[3]) / 2 - config.game_resolution[1] // 2)
                if debug:
                    cv2.arrowedLine(annotated_frame, (config.game_resolution[0] // 2, config.game_resolution[1] // 2), (
                    int((detect_xyxy[0] + detect_xyxy[2]) / 2), int((detect_xyxy[1] + detect_xyxy[3]) / 2)),
                                    (0, 255, 0), 2, tipLength=0.1)
                    cv2.imwrite(os.path.join(save_dir, f"annotated_{detect_object}_{timestep}.jpg"), annotated_frame)
                logger.write(f'pixel is {shoot_x},{shoot_y}')
                shoot(int(shoot_x), int(shoot_y))

                break

def cv_go_hunting(
    total_steps,
    follow_template_files,
    follow_dis_threshold,
    debug=False,
):
    save_dir = config.work_dir
    follow_dis_threshold *= config.resolution_ratio

    model = load_model("./cache/GroundingDINO_SwinT_OGC.py", "./cache/groundingdino_swint_ogc.pth")

    companion = 0
    for step in range(total_steps):
        logger.write(f'Go for hunting #{step}')
        timestep = time.time()

        screen_image_filename, minimap_image_filename = take_screenshot(timestep, config.game_region, config.minimap_region, draw_axis=False)

        # detect wolf as signal: if wolf is detected then hunt; else follow the compainion
        screen, boxes, logits, phrases = groundingDINO_detect(model, screen_image_filename)
        if debug:
            cv2.imwrite(os.path.join(save_dir, f"screen_{timestep}_dino_detect.jpg"),
                        annotate(image_source=screen, boxes=boxes, logits=logits, phrases=phrases))
        h, w, _ = screen.shape
        xyxy = box_convert(boxes=boxes * torch.Tensor([w, h, w, h]), in_fmt="cxcywh", out_fmt="xyxy").numpy().astype(int)


        # find direction to follow
        follow_theta, follow_info = match_template(minimap_image_filename, follow_template_files[companion], config.resolution_ratio, debug)

        if debug:
            logger.debug(f"step {step:03d} | timestep {timestep} done | follow theta: {follow_theta:.2f} | follow distance: {follow_info['distance']:.2f} | follow confidence: {follow_info['confidence']:.3f}")
            cv2.imwrite(os.path.join(save_dir, f"minimap_{timestep}_follow_template.jpg"), follow_info['vis'])

        # cnt = 0
        target_center = (-1, -1)
        num_person, min_person_confidence, min_person_center = 0, 1, (0, 0)
        for detect_xyxy, detect_object, detect_confidence in zip(xyxy, phrases, logits):
            if debug:
                logger.debug(f"step {step:03d} | timestep {timestep} done | detect object: {detect_object} | detect confidence: {detect_confidence:.3f}")
            if 'wolf' == detect_object:
                target_center = (int((detect_xyxy[0] + detect_xyxy[2]) / 2), int((detect_xyxy[1] + detect_xyxy[3]) / 2))
                companion = 1
                logger.write(f'step {step}: switch to follow gray and shoot wolves.')
            if 'person' in detect_object:
                num_person += 1
                if detect_confidence < min_person_confidence:
                    min_person_confidence = detect_confidence
                    min_person_center = (int((detect_xyxy[0] + detect_xyxy[2]) / 2), int((detect_xyxy[1] + detect_xyxy[3]) / 2))

        if sum(target_center) > 0:
            shoot(*target_center)

        if num_person >= 2:
            shoot(*min_person_center)

        if follow_info['distance'] < follow_dis_threshold:
            logger.write('Keep with the companion')


        # elif sum(target_center) > 0 or follow_info['confidence'] > .7:
            # cnt += 1
            # if cnt == 1:
            #     stop_horse()
            # turn(follow_theta)
        # Move
        move_forward(2)
        # time.sleep(.5)
