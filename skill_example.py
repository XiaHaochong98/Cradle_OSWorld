from uac.config import Config
from uac.gameio.lifecycle.ui_control import switch_to_code, switch_to_game
from uac.gameio.composited_skills.navigation import cv_navigation
from uac.gameio.atomic_skills.map import open_map, open_index, close_index
from uac.gameio.atomic_skills.move import turn
import time


if __name__ == "__main__":

    config = Config()

    save_dir = "runs/test1/"
    total_time_step = 1000
    window_bar_height = 30 # 0 # 45
    minimap_extended_side = 432
    screen_region=(0, window_bar_height, config.game_resolution[0], config.game_resolution[1])
    mini_map_region=(70, config.game_resolution[1] - minimap_extended_side - 45 - window_bar_height, minimap_extended_side, minimap_extended_side)

    #navigation
#    switch_to_game()
    
    time.sleep(3)
    cv_navigation(save_dir, total_time_step, screen_region, mini_map_region)

#    switch_to_code()

#    switch_to_game()

    # res_factor = 2560 / 3840 # 0.5
    # prop_move = 90 * res_factor

"""     time.sleep(3)

    prop_move = 90

    while True:
         time.sleep(1)
         turn(prop_move)
         time.sleep(2)
         turn(-1 * prop_move)
 """
#    switch_to_code()

    # map operation 
    # switch_to_game()
    # open_map()
    # time.sleep(1)
    # open_index()
    # time.sleep(1)
    # close_index()
    # time.sleep(1)
    # switch_to_code()
