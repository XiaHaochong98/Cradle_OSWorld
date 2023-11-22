import time

from uac.config import Config
from uac.gameio import IOEnvironment
from uac.gameio.atomic_skills.move import move_forward, turn, stop_horse, mount_horse, dismount_horse
from uac.gameio.lifecycle.ui_control import take_screenshot, segment_minimap, switch_to_game, pause_game, unpause_game
from uac.gameio.composite_skills.navigation import navigate_path
from uac.utils.file_utils import read_resource_file


config = Config()
io_env = IOEnvironment()

class GameManager:

    def __init__(
        self,
        env_name
    ):
        self.env_name = env_name


    def pause_game(self):
        pause_game()


    def unpause_game(self):
        unpause_game()


    def list_bootstrap_skills(self):
        skills = read_resource_file(config.bootstrap_skill_library_path)
        return skills


    def execute_action(self, next_action):
        
        # Execute action
        total_time_step = 500

        if next_action == "navigate_path()":

            time.sleep(3)
            navigate_path(total_time_step)


    def capture_screen(self, include_minimap = False):
        tid = time.time()
        return take_screenshot(tid, include_minimap=include_minimap)
    

    def extract_minimap(self, screenshot_path):
        return segment_minimap(screenshot_path)

