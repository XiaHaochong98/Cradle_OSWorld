import time
import argparse
import math

from uac.gameio import GameManager
from uac.gameio.lifecycle.ui_control import switch_to_code, switch_to_game, segment_minimap, exit_back_to_game
from uac.gameio.composite_skills.navigation import cv_navigation
from uac.gameio.composite_skills.go_to_icon import go_to_horse
from uac.utils.template_matching import match_template_image
from uac.gameio.atomic_skills.map import open_map, open_index, close_index
from uac.gameio.lifecycle.ui_control import unpause_game,pause_game
from uac.gameio.atomic_skills.hunt import shoot,aim
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

#### This will be removed soon. For now, don't delete it. ####
#
#    max = io_env.WIN_NORM_MAX
#    game_w = config.game_resolution[0]
#    game_h = config.game_resolution[1]
#
#    screen_w = config.screen_resolution[0]
#    screen_h = config.screen_resolution[1]
#
#    logger.write("move mid")
#    io_env.mouse_move(0, 0, relative=True)
#    time.sleep(2)
#
#    io_env.mouse_move(config.game_resolution[0]/2, config.game_resolution[1]/2, relative=False)
#    time.sleep(2)
#
#    io_env.mouse_move(0, config.game_resolution[1]/2, relative=False)
#    time.sleep(2)
#
#    io_env.mouse_move(config.game_resolution[0]/2, config.game_resolution[1]/2, relative=False)
#    time.sleep(2)
#
#    y_factor = 0.01
#    iterations_up = 2
#    for i in range(iterations_up):
#
#        q,w = io_env.ahk.mouse_position
#         io_env.ahk.mouse_move(config.game_resolution[0]/2, (0.5*config.game_resolution[1]) - (y_factor*(i+1)*config.game_resolution[1]), speed=0, relative=False)
#        time.sleep(2)
#
#    y_delta = y_factor
#    iterations_down = 10 * iterations_up
#
#    for i in range(iterations_down):
#        i_delta = ((y_delta * config.game_resolution[1]) * (i+1)) / iterations_down
#        io_env.ahk.mouse_move(config.game_resolution[0]/2, (0.5*config.game_resolution[1]) - (y_factor*config.game_resolution[1]) + i_delta, speed=0, relative=False)#
#
#    time.sleep(2)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s',"--skill_chosen",type=str,default="following",help="['navigation', 'go_to_horse', 'map_operation', 'shooting', 'following']"
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
        elif skill_chosen == 'shooting':  # shoot example
            # prompt: "Protect Dutch"
            while True:
                shoot_people()

            # prompt: "Keep the wolves away from Javier and John"
            # shoot_wolves()
        elif skill_chosen == 'following':  # follow companion against wolves example
            # prompt: "Follow Javier"
            # prompt: "Catch up to Javier"
            follow()
