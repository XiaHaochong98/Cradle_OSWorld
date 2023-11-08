import time
import os

from uac.skill_library.atomic_skills.move import turn, move_forward
from uac.utils.angle_estimator import calculate_turn_angle
from uac.utils.UI_control import take_screenshot

def cv_navigation(ahk, save_dir, total_time_step, screen_region=(0,45, 2560, 1600), mini_map_region=(70,1110, 480, 480)):
    os.makedirs(save_dir, exist_ok=True)

    for timestep in range(total_time_step):
        print("timestep", timestep)
        if timestep > 0:
            turn(ahk, turn_angle)
            move_forward(0.5)
            time.sleep(0.2) # avoid running too fast
        
        take_screenshot(save_dir, timestep, screen_region, mini_map_region, draw_axis=True)

        turn_angle = calculate_turn_angle(save_dir, timestep, debug=True)