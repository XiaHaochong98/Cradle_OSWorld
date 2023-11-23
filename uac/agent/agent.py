from typing import List
import json
import time

from uac.config import Config
from uac.log import Logger
from uac.provider.openai import encode_image
from uac.utils.file_utils import assemble_project_path, read_resource_file
from uac.gameio import GameManager
from uac.planner.planner import Planner

config = Config()
logger = Logger()


# Here the Agent using the LLM provider direcly, but we could have a Planner class to wrap the planning prompts.
# This is an incomplete example with not complete quality code, just to bootstrap the repo.

class Agent:

    def __init__(
        self,
        name,
        memory,
        env_manager : GameManager,
        planner : Planner,
    ):
        self.name = name
        self.memory = memory
        self.env_manager = env_manager
        self.planner = planner


    def loop(self):
        
        config.continuous_limit = 1

        # Interaction Loop
        loop_count = 0

        # Example output of information gathering for first image
        context_debug = """
The image shows a scene from the video game Red Dead Redemption 2. It presents a third-person perspective of a character, presumably the protagonist Arthur Morgan, riding a horse. The character is dressed in typical cowboy attire, including a hat, and is equipped with what appears to be a revolver holstered on his right hip, and a satchel slung across his left shoulder. The environment is sunny and seems to be an idyllic forest clearing with a variety of trees, including pines and others with more broad leaves. The atmosphere is serene and there are several horses scattered around the area, suggesting a temporary camp or resting spot for a group.

On the bottom of the image, there's a prompt indicating "Hitch Horse [E]", suggesting that the player on a PC can press the "E" key to hitch their horse to a post or another item intended for that purpose.

As for the minimap on the bottom-left corner, the semi-opaque circular map provides some immediate context for the player's surrounding area:

1. A red path is drawn on the minimap leading from the character's current position towards the northwest direction. This generally indicates a suggested route the player should take to reach a specific destination or objective.
2. There are various icons on the map, including a camp (teepee icon), a mail or delivery point (letter icon), a question mark which might indicate a point of interest or a stranger mission, some facility amenity icons (fork and knife for provisions, a tent for rest or camp upgrades), and a money bag icon which typically represents the camp's contribution box where the player can donate money.
3. The player's character icon is in the center of the minimap, depicted as a white arrow, showing the current direction the character is facing.

The surrounding context of the minimap is vital for in-game navigation and decision-making. Based on the minimap, the player seems to be in a campsite or has just exited one. They have a clear destination set to the northwest, and based on the surrounding icons, there are several amenities and potential interactions available to them within the camp.
"""

        # Start interaction loop
        while True:

            # Stop if limit is reached
            loop_count += 1
            if (
                config.continuous_mode and 
                config.continuous_limit > 0 and
                loop_count > config.continuous_limit
            ):
                logger.write(f"Continuous Limit Reached: {config.continuous_limit} iteractions")
                break

            # Get environment input
            image = self.env_manager.capture_screen()
            self.env_manager.pause_game()

            debug = True
            if debug:
                image = "./runs/camp-on-horse-red-line-000.jpg" # Example of image with a red-line
                image = assemble_project_path(image)
            
            # Prepare info gathering
            info_response = ""

            result_str = self.planner._gather_information(image_files=[image])
            info_response = json.loads(result_str)["description"]

            # Prepare decision making

            # @TODO: Goal and previous_actions need to be hooked on integration between iteration
            # In this first case, once we have map manipulation
            goal = "Go to store."
            skills = self.env_manager.list_bootstrap_skills()
            previous_actions = "[add_map_waypoint()]"
            output_format = read_resource_file("./res/prompts/output_example/decision_making.json")

            # Context should use the description from the gather_information response
            debug = True
            if debug:
                context = context_debug
            else:
                context = info_response

            decision_response = ""

            args = {"context" : context, "goal" : goal, "skills" : skills, "previous_actions" : previous_actions, "output_format" : output_format}

            result_str = self.planner._decision_making(input=args, image_files=[image])
            decision_response = result_str

            # Example output of decision making for first image
            decision_output_debug = """
{
   "skill_steps": ["navigate_path()"],
   "reason": "After adding a waypoint, the player should now navigate along the red path shown on the minimap towards the location set. Since the goal is to go to a store, and the red path is likely leading out of the camp and towards the nearest town where stores are usually located, following the path will progress towards reaching a store."
}
"""

            # Action should use the output from the decision making response
            debug = True
            if debug:
                output = decision_output_debug
            else:
                output = decision_response

            # Action extraction and execution
            next_action = extract_next_action(output)

            time.sleep(3)
            self.env_manager.unpause_game()
            time.sleep(1)
            self.env_manager.execute_action(next_action)
            time.sleep(5)
            post_action_image = self.env_manager.capture_screen(include_minimap=False)[0]
            self.env_manager.pause_game()

            debug = True
            if debug:
                image = "./res/samples/screen_redline.jpg"
                post_action_image = "./res/samples/screen_no_redline.jpg"

            # Prepare success detection

            image_descriptions = "the images sent to you are: 1. the screenshot from the previous timestep, and 2. the screenshot for the current observation"
            images = [image, post_action_image]
            output_format = read_resource_file("./res/prompts/output_example/success_detection.json")

            args = {"goal" : goal, "image_paths" : images, "image_descriptions" : image_descriptions, "output_format" : output_format}

            result = self.planner._success_detection(input=args, image_files=images)

            # Check success
            success = result["success"]

            # @TODO represent new state for next loop
            # @TODO re-use post-action image for info gathering?

            logger.write() #end of loop


def to_text(template_str: str = None, params: dict = None) -> str:

    str = template_str

    if template_str is None or params is None:
        return str

    keys = params.keys()
    for key in keys:
        if key in template_str:            
            str = str.replace(f'<${key}$>', params[key])

    return str


def extract_next_action(json_input):

    task_dict = json.loads(json_input)

    # Extract the first action of the sub-task_name
    key = "skill_steps" # list(task_dict.keys())[0]
    first_action = task_dict[key][0] if task_dict[key] else None

    logger.debug(f"The first action in the '{key}' list is: {first_action}")

    return first_action
