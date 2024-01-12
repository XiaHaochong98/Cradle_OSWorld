import time

from uac.config import Config
from uac.gameio import IOEnvironment
from uac.log import Logger
from uac.gameio.lifecycle.ui_control import take_screenshot, segment_minimap, switch_to_game, pause_game, unpause_game, exit_back_to_pause
from uac.gameio.composite_skills.navigation import navigate_path
from uac.gameio.skill_registry import SkillRegistry
from typing import Tuple


config = Config()
logger = Logger()
io_env = IOEnvironment()


class GameManager:

    def __init__(
        self,
        env_name,
        embedding_provider = None
    ):
        self.env_name = env_name
        self.skill_registry = SkillRegistry(local_path = config.skill_local_path, 
                                            from_local = config.skill_from_local,
                                            store_path = config.work_dir,
                                            skill_scope = config.skill_scope,
                                            embedding_provider = embedding_provider)


    def pause_game(self):
        pause_game()


    def unpause_game(self):
        unpause_game()


    def switch_to_game(self):
        switch_to_game()


    def exit_back_to_pause(self):
        exit_back_to_pause()


    def list_bootstrap_skills(self):

        all_skills = self.skill_registry.get_all_skills()
        return self.get_filtered_skills(all_skills)


    def get_filtered_skills(self, skill_list):

        filtered_skill_library = []

        for skill_name in skill_list:
            skill_item = self.skill_registry.get_from_skill_library(skill_name)
            filtered_skill_library.append(skill_item)

        return filtered_skill_library


    def add_new_skill(self, skill_code, overwrite = False):
        return self.skill_registry.register_skill_from_code(skill_code = skill_code, overwrite = overwrite)


    def delete_skill(self, skill_name):
        self.skill_registry.delete_skill(skill_name)


    def retrieve_skills(self, query_task, skill_num):
        return self.skill_registry.retrieve_skills(query_task, skill_num)


    def register_available_skills(self, candidates):
        self.skill_registry.register_available_skills(candidates)


    def get_skill_library_in_code(self, skill) -> Tuple[str, str]:
        return self.skill_registry.get_skill_library_in_code(skill)


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
            "errors" : False,
            "errors_info": ""
        }

        if len(actions) == 0:
            logger.warn(f"No actions to execute!")
            exec_info["errors"] = True
            exec_info["errors_info"] = "No actions to execute!"
            return exec_info

        try: 
            #switch_to_game()
            for skill in actions:

                skill_name, skill_params = self.skill_registry.convert_expression_to_skill(skill)

                logger.write(f"Executing skill: {skill_name} with params: {skill_params}")

                # Enable OCR for composite skills, start the ocr check
                if skill_name in config.ocr_check_composite_skill_names:
                    config.ocr_different_previous_text = False
                    config.enable_ocr = True

                if "navigate" in skill_name:
                    self.execute_navigation(skill_name)
                else:
                    self.skill_registry.execute_skill(name=skill_name, params=skill_params)

                exec_info["executed_skills"].append(skill_name)
                exec_info["last_skill"] = skill_name

                self.post_action_wait()
                logger.write(f"Finished executing skill: {skill_name} and wait.")

        except Exception as e:
            logger.error(f"Error executing skill: {e}")
            exec_info["errors"] = True
            exec_info["errors_info"] = f"Error executing skill: {e}"

        return exec_info


    # Currently all actions have wait in them, if needed
    def post_action_wait(self):
    #    time.sleep(config.POST_ACTION_WAIT_TIME)
    #    time.sleep(0.5)
        time.sleep(1)


    def capture_screen(self, include_minimap = False):
        #switch_to_game()
        tid = time.time()
        return take_screenshot(tid, include_minimap=include_minimap)


    def extract_minimap(self, screenshot_path):
        return segment_minimap(screenshot_path)


    def list_session_screenshots(self, session_dir: str = config.work_dir):
        return io_env.list_session_screenshots(session_dir)


    def store_skills(self):
        self.skill_registry.store_skills()

