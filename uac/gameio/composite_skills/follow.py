import time, os
import cv2

from uac.config import Config
from uac.log import Logger
from uac.gameio.atomic_skills.move import turn, move_forward
from uac.gameio.lifecycle.ui_control import take_screenshot, pause_game, unpause_game, CircleDetector
from uac.gameio.skill_registry import register_skill

config = Config()
logger = Logger()

MAX_FOLLOW_ITERATIONS = 300


@register_skill("follow")
def follow():
    """
    Follow target on the minimap.
    """
    cv_follow_circles(MAX_FOLLOW_ITERATIONS, debug=False)


def cv_follow_circles(
        iterations,
        follow_dis_threshold=50,
        debug=False,
):
    '''
    Prioritize following the yellow circle. If not detected, then follow the gray circle.
    '''
    save_dir = config.work_dir
    follow_dis_threshold *= config.resolution_ratio

    is_move = False
    circle_detector = CircleDetector(config.resolution_ratio)

    move_forward(3)

    for step in range(iterations):
        if debug:
            logger.write(f'Go for hunting #{step}')

        if config.ocr_different_previous_text:
            logger.write("The text is different from the previous one.")
            config.ocr_enabled = False # disable ocr
            config.ocr_different_previous_text = False  # reset
            break

        timestep = time.time()

        screen_image_filename, minimap_image_filename = take_screenshot(timestep, config.game_region,
                                                                        config.minimap_region, draw_axis=False)

        # find direction to follow
        follow_theta, follow_info = circle_detector.detect(minimap_image_filename, debug=debug)

        if debug:
            logger.debug(
                f"step {step:03d} | timestep {timestep} done | follow theta: {follow_theta:.2f} | follow distance: {follow_info['distance']:.2f} | follow confidence: {follow_info['confidence']:.3f}")
            cv2.circle(follow_info['vis'], follow_info['center'], 1, (0, 255, 0), 2)
            cv2.imwrite(os.path.join(save_dir, f"minimap_{timestep}_follow_template.jpg"), follow_info['vis'])

        if debug and follow_info['distance'] < follow_dis_threshold:
            logger.write('Keep with the companion')

        if abs(follow_theta) <= 360:
            turn(follow_theta)
            if not is_move:
                move_forward(0.8)
                is_move = True
            else:
                move_forward(0.3)
        else:
            is_move = False


__all__ = [
    "follow",
]


