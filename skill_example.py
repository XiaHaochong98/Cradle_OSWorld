import time
import argparse

from uac.gameio.lifecycle.ui_control import switch_to_code, switch_to_game, take_screenshot, segment_minimap, pause_game, unpause_game, exit_back_to_game
from uac.gameio.composite_skills.navigation import cv_navigation
from uac.gameio.composite_skills.go_to_icon import go_to_horse
from uac.utils.template_matching import match_template_image
from uac.gameio.atomic_skills.map import open_map, open_index, close_index
from uac.gameio.atomic_skills.move import turn, mount_horse
from uac.gameio.composite_skills.follow import follow
from uac.gameio.composite_skills.auto_shoot import shoot_wolves, shoot_people
from uac.config import Config
from uac.log import Logger
from uac.log.logger import shrink_log_message

config = Config()
logger = Logger()


class SwitchWindow(object):
    def __enter__(self):
        switch_to_game()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # switch_to_code()
        pass


if __name__ == "__main__":

    # c_text = shrink_log_message(text)
    # logger.write(c_text)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skill_chosen",type=str,default="following",help="['navigation', 'go_to_horse', 'map_operation', 'shooting', 'following']"
    )
    args = parser.parse_args()
    skill_chosen = args.skill_chosen
    debug = True

    # gm = GameManager(config.env_name)
    # time.sleep(3)
    # gm.execute_action("navigate_path()")

    with SwitchWindow():
        if skill_chosen == 'navigation':  # navigation example, you need to have a red line in the mini-map first
            cv_navigation(1000, debug=debug)
        elif skill_chosen == 'go_to_horse':  # find-and-get-on-horse example
            go_to_horse()
            mount_horse()
            time.sleep(3)
        elif skill_chosen == 'map_operation':  # map operation example
            open_map()
            time.sleep(1)
            open_index()
            time.sleep(1)
            close_index()
            time.sleep(1)
        elif skill_chosen == 'shooting':  # shoot wolves example
            # prompt: "Keep the wolves away from Javier and John"
            shoot_people()
            shoot_wolves()
        elif skill_chosen == 'following':  # follow companion against wolves example
            # prompt: "Follow Javier"
            # prompt: "Catch up to Javier"
            follow()



