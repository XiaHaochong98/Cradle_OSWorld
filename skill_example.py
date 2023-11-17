from uac.config import Config
from uac.gameio.lifecycle.ui_control import switch_to_code, switch_to_game
from uac.gameio.composited_skills.navigation import cv_navigation
from uac.gameio.atomic_skills.map import open_map, open_index, close_index
from uac.gameio.atomic_skills.move import turn
import time
import os


if __name__ == "__main__":

    config = Config()

    save_dir = "runs/test1/"
    os.makedirs(save_dir, exist_ok=True)
    total_time_step = 1000

    switch_to_game()
    cv_navigation(save_dir, total_time_step, config.game_region, config.mini_map_region)
    switch_to_code()

    # map operation 
    # switch_to_game()
    # open_map()
    # time.sleep(1)
    # open_index()
    # time.sleep(1)
    # close_index()
    # time.sleep(1)
    # switch_to_code()
