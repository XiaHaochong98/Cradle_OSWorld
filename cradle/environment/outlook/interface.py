from cradle.config import Config
from cradle.log import Logger
from cradle.gameio import IOEnvironment

from cradle.environment.outlook.lifecycle.ui_control import take_screenshot, switch_to_game, pause_game, unpause_game
from cradle.environment.outlook.skill_registry import SkillRegistry
from cradle.environment import register_environment

config = Config()
logger = Logger()
io_env = IOEnvironment()


@register_environment("outlook")
class Interface():

    def __init__(self):

        # load ui control in lifecycle
        self.take_screenshot = take_screenshot
        self.switch_to_game = switch_to_game
        self.pause_game = pause_game
        self.unpause_game = unpause_game

        # load skill registry
        self.SkillRegistry = SkillRegistry

        # init planner parms
        self.planner_params = {
            "__check_list__": [
                "decision_making",
                "gather_information",
                "success_detection",
                "self_reflection",
                "information_summary",
                "gather_text_information"
            ],
            "prompt_paths": {
                "inputs": {
                    "decision_making": "./res/outlook/prompts/inputs/decision_making.json",
                    "gather_information": "./res/outlook/prompts/inputs/gather_information.json",
                    "success_detection": "./res/outlook/prompts/inputs/success_detection.json",
                    "self_reflection": "./res/outlook/prompts/inputs/self_reflection.json",
                    "information_summary": "./res/outlook/prompts/inputs/information_summary.json",
                    "gather_text_information": "./res/outlook/prompts/inputs/gather_text_information.json"
                },
                "templates": {
                    "decision_making": "./res/outlook/prompts/templates/decision_making.prompt",
                    "gather_information": "./res/outlook/prompts/templates/gather_information.prompt",
                    "success_detection": "./res/outlook/prompts/templates/success_detection.prompt",
                    "self_reflection": "./res/outlook/prompts/templates/self_reflection.prompt",
                    "information_summary": "./res/outlook/prompts/templates/information_summary.prompt",
                    "gather_text_information": "./res/outlook/prompts/templates/gather_text_information.prompt"
                },
            }
        }

        # init skill library
        self.skill_library = []

        # init task description
        self.task_description = ""
