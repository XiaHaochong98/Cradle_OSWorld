import time
import argparse
import math

from uac.gameio import GameManager
from uac.gameio.lifecycle.ui_control import switch_to_code, switch_to_game, segment_minimap, exit_back_to_game
from uac.gameio.composite_skills.navigation import cv_navigation
from uac.gameio.composite_skills.go_to_icon import go_to_horse
from uac.utils.template_matching import match_template_image
from uac.gameio.atomic_skills.map import open_map, open_index, close_index
from uac.gameio.lifecycle.ui_control import unpause_game, pause_game
from uac.gameio.atomic_skills.combat import shoot, aim, fight
from uac.gameio.atomic_skills.move import turn, mount_horse, move_forward
from uac.gameio.composite_skills.follow import follow
from uac.gameio.composite_skills.auto_shoot import shoot_wolves, shoot_people
from uac.gameio.skill_registry import SkillRegistry
from uac.config import Config
from uac.log import Logger
from uac.gameio import IOEnvironment
from uac.log.logger import shrink_log_message
from uac.gameio.io_env import IOEnvironment, _theta_calculation

config = Config()
logger = Logger()
io_env = IOEnvironment()


class SwitchWindow(object):
    def __enter__(self):
        switch_to_game()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # switch_to_code()
        pass


if __name__ == "__main__":

    gm = GameManager(config.env_name)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s',"--skill_chosen",type=str,default="following",help="['navigation', 'go_to_horse', 'map_operation', 'shoot_people', 'shoot_wolves', 'following']"
    )
    args = parser.parse_args()
    skill_chosen = args.skill_chosen
    debug = True

    gm = GameManager(config.env_name)

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
        elif skill_chosen == 'shoot_people':  # shoot example
            # prompt: "Protect Dutch"
            shoot_people()

        elif skill_chosen == 'shoot_wolves':  # shoot example
            # prompt: "Keep the wolves away from Javier and John"
            shoot_wolves()

        elif skill_chosen == 'following':  # follow companion against wolves example
            # prompt: "Follow Javier"
            # prompt: "Catch up to Javier"
            follow()
