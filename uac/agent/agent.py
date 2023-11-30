from typing import List
import json
import time

from uac.config import Config
from uac.log import Logger
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
        
        logger.write(f"Starting {self.name} loop w/ env {config.env_name}")

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

            images_info = [
                {
                    "introduction": "This is a screenshot of the current moment in the game",
                    "path": image,
                    "assistant": ""
                }
            ]
            image_introduction = images_info

            output_format = read_resource_file("./res/prompts/api_output/gather_information.json")
            args = {"output_format": output_format, "image_introduction": image_introduction}

            # data = self.planner.gather_information(input=args)
            # info_response = data["res_dict"]["description"]

            # Prepare decision making

            # @TODO: Goal and previous_actions need to be hooked on integration between iteration
            # In this first case, once we have map manipulation
            task_description = "Go to store."
            skill_library = self.env_manager.list_bootstrap_skills() # @TODO may have to change format
            previous_actions = "[add_map_waypoint()]"
            output_format = read_resource_file("./res/prompts/api_output/decision_making.json")

            images_info = [
                {
                    "introduction": "This is a screenshot of the current moment in the game",
                    "path": image,
                    "assistant": ""
                }
            ]
            image_introduction = images_info

            # Context should use the description from the gather_information response
            debug = True
            if debug:
                context = context_debug
            else:
                context = info_response

            args = {"context" : context, "task_description" : task_description, "skill_library" : skill_library, "previous_actions" : previous_actions, "output_format" : output_format, "image_introduction": image_introduction}

            skills = []

            # data = self.planner.decision_making(input=args)
            # skills = data['outcome']

            if skills is None:
                skills = []

            logger.write(f'R: {skills}')

            # Example output of decision making for first image
            decision_output_debug = ["navigate_path()"]

            # Action should use the output from the decision making response
            debug = True
            if debug:
                skill_steps = decision_output_debug
            else:
                skill_steps = skills

            skill_steps = skill_steps[:1]

            skill_steps = ['turn(theta=30)', 'move_forward(duration=1)', 'turn(theta=90)', 'move_forward(duration=3)']

            logger.write(f'Skill Steps: {skill_steps}')

            exec_info = self.env_manager.execute_actions(skill_steps)

            pre_skill = exec_info["last_skill"] # exec_info also has the list of successfully executed skills. skill_steps is the full list, which may differ if there were execution errors.

            post_action_image = self.env_manager.capture_screen(include_minimap=False)[0]
            self.env_manager.pause_game()

            debug = True
            if debug:
                image = "./res/samples/screen_redline.jpg"
                post_action_image = "./res/samples/screen_no_redline.jpg"

            # Prepare success detection
            output_format = read_resource_file("./res/prompts/api_output/success_detection.json")

            images_info = [
                {
                    "introduction": "This is a screenshot of the current moment in the game",
                    "path": image,
                    "assistant": ""
                },
                {
                    "introduction": "This screenshot is the current observation",
                    "path": post_action_image,
                    "assistant": ""
                }
            ]
            image_introduction = images_info

            args = {"task_description" : task_description, "output_format" : output_format, "image_introduction": image_introduction}

            # data = self.planner.success_detection(input=args)

            # # Check success
            # res_dict = data['res_dict']
            # reason = res_dict['decision']['reason']
            # success = data['outcome']

            # logger.write(f'Success: {success}')
            # logger.write(f'Reason: {reason}')

            # @TODO represent new state for next loop
            # @TODO re-use post-action image for info gathering?

            logger.write() #end of loop
