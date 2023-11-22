import time

from uac.gameio.game_manager import GameManager
from uac.gameio.lifecycle.ui_control import switch_to_code, switch_to_game, take_screenshot, segment_minimap, pause_game, unpause_game
from uac.gameio.composite_skills.navigation import cv_navigation
from uac.gameio.composite_skills.go_to_icon import cv_go_to_icon
from uac.utils.template_matching import match_template_image
from uac.gameio.atomic_skills.map import open_map, open_index, close_index
from uac.gameio.atomic_skills.move import turn, mount_horse
from uac.config import Config

config = Config()


if __name__ == "__main__":

    total_time_steps = 1000

    # gm = GameManager(config.env_name)
    # time.sleep(3)
    # gm.execute_action("navigate_path()")

    # switch_to_game()
    # cv_navigation(total_time_steps)
    # switch_to_code()

    switch_to_game()

    # you need to have a red line in the mini-map first
    # find-and-get-on-horse example
    horse_template_file = './res/icons/horse.jpg'
    cv_go_to_icon(total_time_steps, horse_template_file, debug=True)

    mount_horse()
    time.sleep(3)

    cv_navigation(total_time_steps, terminal_threshold=120)
    switch_to_code()

    # pause_game()

    # # find-and-get-on-horse example
    # horse_template_file = './res/icons/horse.jpg'
    # switch_to_game()    
    # cv_go_to_icon(total_time_steps, horse_template_file, debug=True)
    # switch_to_code()

    # map operation 
    # switch_to_game()
    # open_map()
    # time.sleep(1)
    # open_index()
    # time.sleep(1)
    # close_index()
    # time.sleep(1)
    # switch_to_code()


