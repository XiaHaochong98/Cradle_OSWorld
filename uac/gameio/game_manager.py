import time

from uac.config import Config
from uac.gameio import IOEnvironment
from uac.log import Logger
from uac.gameio.lifecycle.ui_control import take_screenshot, segment_minimap, switch_to_game, pause_game, unpause_game, exit_back_to_pause
from uac.gameio.composite_skills.navigation import navigate_path
from uac.gameio.skill_registry import SKILL_REGISTRY, get_skill_library, convert_expression_to_skill, execute_skill

config = Config()
logger = Logger()
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


    def switch_to_game(self):
        switch_to_game()


    def exit_back_to_pause(self):
        exit_back_to_pause()


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

        exec_info = {
            "executed_skills" : [],
            "last_skill" : '',
            "errors" : False
        }

        if len(actions) == 0:
            logger.warn(f"No actions to execute!")
            return exec_info

        try: 
            #switch_to_game()
            for skill in actions:
                
                skill_name, skill_params = convert_expression_to_skill(skill)
                
                logger.write(f"Executing skill: {skill_name} with params: {skill_params}")

                if "navigate" in skill_name:
                    self.execute_navigation(skill_name)
                else:
                    execute_skill(name=skill_name, params=skill_params)
                
                exec_info["executed_skills"].append(skill_name)
                exec_info["last_skill"] = skill_name

                self.post_action_wait()
                logger.write(f"Finished executing skill: {skill_name} and wait.")

        except Exception as e:
            logger.error(f"Error executing skill: {e}")
            exec_info["errors"] = True

        return exec_info


    # Currently all actions have wait in them, if needed
    def post_action_wait(self):
    #    time.sleep(config.POST_ACTION_WAIT_TIME)
        time.sleep(0.5)


    def capture_screen(self, include_minimap = False):
        #switch_to_game()
        tid = time.time()
        return take_screenshot(tid, include_minimap=include_minimap)
    

    def extract_minimap(self, screenshot_path):
        return segment_minimap(screenshot_path)


    def list_session_screenshots(self, session_dir: str = config.work_dir):
        return io_env.list_session_screenshots(session_dir)

