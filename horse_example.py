from uac.config import Config
from uac.gameio.lifecycle.ui_control import switch_to_code, switch_to_game
from uac.gameio.composite_skills.find_get_on_horse import find_get_on_horse_cv
from uac.utils.template_matching import match
import os
from glob import glob


if __name__ == "__main__":
    print()
    config = Config()

    save_dir = "runs/test2/"
    os.makedirs(save_dir, exist_ok=True)
    total_time_step = 200
    # screen_region = (0, 45, 2560, 1600),
    # mini_map_region = (70, 1110, 480, 480),
    # minimap_origin_coord = (176, 263)
    horse_template_file = './res/icons/horse.png'
    pause_clock_template_file = './res/icons/clock.png'

    switch_to_game()
    # find-and-get-on-horse example
    find_get_on_horse_cv(save_dir, total_time_step, horse_template_file, config.game_region, config.mini_map_region, debug=True)
    # multiple-scale-template-matching example, decide whether the game is paused according to the confidence score
    match_info = match(glob(save_dir + 'screen_*.jpg')[-1], pause_clock_template_file,save_dir + 'clock_match.json')
    switch_to_code()