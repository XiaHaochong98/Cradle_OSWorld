from cradle.config import Config
from cradle.log import Logger
from cradle.gameio import IOEnvironment
from cradle.environment.osworld.lifecycle.ui_control import pause_game, unpause_game
from cradle.environment.osworld.skill_registry import SkillRegistry
from cradle.environment import register_environment
from cradle.utils.image_utils import draw_mouse_pointer
import cradle.environment.osworld.atomic_skills
import cradle.environment.osworld.composite_skills

config = Config()
logger = Logger()
io_env = IOEnvironment()


@register_environment("osworld")
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
                    "decision_making": "./res/osworld/prompts/inputs/decision_making.json",
                    "gather_information": "./res/osworld/prompts/inputs/gather_information.json",
                    "success_detection": "./res/osworld/prompts/inputs/success_detection.json",
                    "self_reflection": "./res/osworld/prompts/inputs/self_reflection.json",
                    "information_summary": "./res/osworld/prompts/inputs/information_summary.json",
                    "gather_text_information": "./res/osworld/prompts/inputs/gather_text_information.json"
                },
                "templates": {
                    "decision_making": "./res/osworld/prompts/templates/decision_making.prompt",
                    "gather_information": "./res/osworld/prompts/templates/gather_information.prompt",
                    "success_detection": "./res/osworld/prompts/templates/success_detection.prompt",
                    "self_reflection": "./res/osworld/prompts/templates/self_reflection.prompt",
                    "information_summary": "./res/osworld/prompts/templates/information_summary.prompt",
                    "gather_text_information": "./res/osworld/prompts/templates/gather_text_information.prompt"
                },
            }
        }

        # init skill library
        # @ Pengjie register skills here
        self.skill_library = [
            "click_at_position",
            "mouse_drag",
            "type_text",
            "press_key",
            "save_page",
            "return_to_previous_page",
            "press_keys_combined",
            "click_on_label",
            "go_back_to_target_application",
            "zoom_in",
            "zoom_out",
        ]

        # init task description
        self.task_description = ""
