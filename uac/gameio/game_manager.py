import time

from uac.config import Config
from uac.gameio import IOEnvironment
from uac.log import Logger
from uac.gameio.atomic_skills.move import move_forward, turn, stop_horse, mount_horse, dismount_horse
from uac.gameio.lifecycle.ui_control import take_screenshot, segment_minimap, switch_to_game, pause_game, unpause_game
from uac.gameio.composite_skills.navigation import navigate_path
from uac.utils.file_utils import read_resource_file
from uac.gameio.skill_registry import SKILL_REGISTRY, get_skill_library, convert_expression_to_skill, execute_skill

config = Config()
logger = Logger()
io_env = IOEnvironment()


class GameManager:

    POST_ACTION_WAIT_TIME = 4

    def __init__(
        self,
        env_name
    ):
        self.env_name = env_name


    def pause_game(self):
        pause_game()


    def unpause_game(self):
        unpause_game()


    def switch_to_game(self):
        switch_to_game()


    def list_bootstrap_skills(self):
        
        all_skills = list(SKILL_REGISTRY.keys())
        return self.get_filtered_skills(all_skills)


    def get_filtered_skills(self, skill_list):

        filtered_skill_library = []

        for skill_name in skill_list:
            skill_item = get_skill_library(SKILL_REGISTRY[skill_name])
            filtered_skill_library.append(skill_item)

        return filtered_skill_library


    def execute_navigation(self, action):
        
        # Execute action
        total_time_step = 500

        if action == "navigate_path":

            time.sleep(3)
            navigate_path(total_time_step)


    def execute_actions(self, actions):

        last_skill = ""
        errors = False

        if len(actions) == 0:
            logger.error(f"No actions to execute!")
            return True, None

        try: 
            for skill in actions:
                
                skill_name, skill_params = convert_expression_to_skill(skill)
                
                logger.write(f"Executing skill: {skill_name} with params: {skill_params}")

                switch_to_game()
                time.sleep(1)
                unpause_game()
                time.sleep(1)

                if "navigate" in skill_name:
                    self.execute_navigation(skill_name)
                else:
                    execute_skill(name=skill_name, params=skill_params)
                
                last_skill = skill_name
                
                self.post_action_wait()

        except Exception as e:
            logger.error(f"Error executing skill: {e}")
            errors = True

        return errors, last_skill


    def post_action_wait(self):
        time.sleep(self.POST_ACTION_WAIT_TIME)


    def capture_screen(self, include_minimap = False):
        switch_to_game()
        tid = time.time()
        return take_screenshot(tid, include_minimap=include_minimap)
    

    def extract_minimap(self, screenshot_path):
        return segment_minimap(screenshot_path)


    def list_session_screenshots(self, session_dir: str = config.work_dir):
        return io_env.list_session_screenshots(session_dir)
