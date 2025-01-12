from cradle.config import Config
from cradle.log import Logger
from cradle.gameio import IOEnvironment
from cradle.environment.capcut.lifecycle.ui_control import pause_game, unpause_game
from cradle.environment.capcut.skill_registry import SkillRegistry
from cradle.environment import register_environment
from cradle.utils.image_utils import draw_mouse_pointer
import cradle.environment.capcut.atomic_skills
import cradle.environment.capcut.composite_skills

config = Config()
logger = Logger()
io_env = IOEnvironment()


@register_environment("capcut")
class Interface():

    def draw_mouse_pointer(self, frame, x, y):
        return draw_mouse_pointer(frame, x, y)


    def __init__(self):

        # load UI control in lifecycle
        self.pause_game = pause_game
        self.unpause_game = unpause_game
        self.augment_image = self.draw_mouse_pointer

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
                    "decision_making": "./res/capcut/prompts/inputs/decision_making.json",
                    "gather_information": "./res/capcut/prompts/inputs/gather_information.json",
                    "success_detection": "./res/capcut/prompts/inputs/success_detection.json",
                    "self_reflection": "./res/capcut/prompts/inputs/self_reflection.json",
                    "information_summary": "./res/capcut/prompts/inputs/information_summary.json",
                    "gather_text_information": "./res/capcut/prompts/inputs/gather_text_information.json"
                },
                "templates": {
                    "decision_making": "./res/capcut/prompts/templates/decision_making.prompt",
                    "gather_information": "./res/capcut/prompts/templates/gather_information.prompt",
                    "success_detection": "./res/capcut/prompts/templates/success_detection.prompt",
                    "self_reflection": "./res/capcut/prompts/templates/self_reflection.prompt",
                    "information_summary": "./res/capcut/prompts/templates/information_summary.prompt",
                    "gather_text_information": "./res/capcut/prompts/templates/gather_text_information.prompt"
                },
            }
        }

        # init skill library
        self.skill_library = [
            "click_at_position",
            "mouse_drag",
            "type_text",
            "press_key",
            "press_keys_combined",
            "click_on_label",
            "mouse_drag_with_label",
            "move_timeline_forward",
            "move_timeline_backward"
        ]

        # init task description
        self.task_description = ""
