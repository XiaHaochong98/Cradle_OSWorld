from uac.utils.UI_control import switch_to_code, switch_to_game
from uac.skill_library.composited_skills.navigation import cv_navigation
from uac.skill_library.atomic_skills.map import open_map, open_index, close_index
from ahk import AHK
import time

if __name__ == "__main__":
    save_dir = "runs/test1/"
    total_time_step = 1000
    screen_region=(0,45, 2560, 1600)
    mini_map_region=(70,1110, 480, 480)

    #navigation
    ahk = AHK()
    switch_to_game()
    cv_navigation(ahk, save_dir, total_time_step, screen_region, mini_map_region)
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
