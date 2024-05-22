from cradle.config import Config
from cradle.log import Logger
from cradle.gameio import IOEnvironment
from cradle.environment.osworld.lifecycle.ui_control import pause_game, unpause_game
from cradle.environment.osworld.skill_registry import SkillRegistry
from cradle.environment import register_environment
from cradle.utils.image_utils import draw_mouse_pointer
import cradle.environment.osworld.atomic_skills
# import cradle.environment.osworld.composite_skills
from cradle.environment.osworld.atomic_skills import (
move_to_position,
click,
mouse_down,
mouse_up,
right_click,
double_click,
drag_to_position,
scroll,
type_text,
press_key,
key_down,
key_up,
press_hotkey,
)

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
        self.move_to_position = move_to_position
        self.click = click
        self.mouse_down = mouse_down
        self.mouse_up = mouse_up
        self.right_click = right_click
        self.double_click = double_click
        self.drag_to_position = drag_to_position
        self.scroll = scroll
        self.type_text = type_text
        self.press_key = press_key
        self.key_down = key_down
        self.key_up = key_up
        self.press_hotkey = press_hotkey

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
            "move_to_position",
            "click",
            "mouse_down",
            "mouse_up",
            "right_click",
            "double_click",
            "drag_to_position",
            "scroll",
            "type_text",
            "press_key",
            "key_down",
            "key_up",
            "press_hotkey",
        ]

        # init task description
        self.task_description = ""