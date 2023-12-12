from typing import List
import json
import time

from uac.config import Config
from uac.log import Logger
from uac.utils.file_utils import assemble_project_path, read_resource_file
from uac.utils.json_utils import load_json
from uac.gameio import GameManager
from uac.planner.planner import Planner
from uac.memory.interface import MemoryInterface
from uac.gameio.atomic_skills.map import __all__ as map_skills
from uac.gameio.atomic_skills.buy import __all__ as buy_skills
from uac.gameio.atomic_skills.trade_utils import __all__ as trade_skills
from uac.gameio.atomic_skills.move import __all__ as move_skills
from uac.gameio.composite_skills.navigation import __all__ as nav_skills
from uac.gameio.composite_skills.go_to_icon import __all__ as go_skills


config = Config()
logger = Logger()

# Here the Agent using the LLM provider direcly, but we could have a Planner class to wrap the planning prompts.
# This is an incomplete example with not complete quality code, just to bootstrap the repo.

def decision_making_args(planner, memory):
        
    input = planner.decision_making_.input_map
    input["task_description"] = memory.get_recent_history("task_description", k=1)[0]
    
    image_introduction = [
        {
            "introduction": input["image_introduction"][-2]["introduction"],
            "path": memory.get_recent_history("image", k=2)[0],
            "assistant": input["image_introduction"][-2]["assistant"]
        },
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": memory.get_recent_history("image", k=1)[0],
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]
    input["image_introduction"] = image_introduction
    input["previous_action"] = memory.get_recent_history("action", k=1)[-1]
    input["previous_reasoning"] = memory.get_recent_history("decision_making_reasoning", k=1)[-1]
    input['skill_library'] = memory.get_recent_history("skill_library", k=1)[-1]
    return input

def success_detection_args(planner, memory):
        
    input = planner.success_detection_.input_map
    input["task_description"] = memory.get_recent_history("task_description", k=1)[0]
    
    image_introduction = [
        {
            "introduction": input["image_introduction"][-2]["introduction"],
            "path": memory.get_recent_history("image", k=2)[0],
            "assistant": input["image_introduction"][-2]["assistant"]
        },
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": memory.get_recent_history("image", k=1)[0],
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]
    input["image_introduction"] = image_introduction
    input["previous_action"] = memory.get_recent_history("action", k=1)[-1]
    input["previous_reasoning"] = memory.get_recent_history("decision_making_reasoning", k=1)[-1]
    return input

class Agent:

    def __init__(
        self,
        name,
        memory : MemoryInterface,
        gm : GameManager,
        planner : Planner
    ):
        self.name = name
        self.memory = memory
        self.gm = gm
        self.planner = planner


    def loop(self):
        
        config.continuous_limit = 10

        # Interaction Loop
        loop_count = 0

        last_executed_skill = None
        
        current_sub_task = None
        sub_task_args = None
        
        sub_task_index = 0

        # @TODO HACK 
        decomposed_task_steps          = ["Go to the horse and mount it", 
                                          "Create waypoint to the saloon", 
                                          "Follow the red line to the saloon", 
                                          "Create waypoint to the store", 
                                          "Follow the red line to the store", 
                                          "Enter the store",  
                                          "Approach shopkeeper",      
                                          "Buy apple"]
        
        decomposed_task_description = ["Your task is to go mount the horse.",  
                                       "Mark the \"Saloon\" on a Map as the Waypoint via the Index.", 
                                       "Go to the \"Saloon\"",
                                       "Mark the \"General Store\" on a Map as the Waypoint via the Index.", 
                                       "Go to the \"General Store\"",
                                       "Your task is to enter the general store.",
                                       "Your task is to get close to the shopkeeper.", 
                                       "Your task is to buy one 'APPLE'."]
        decomposed_task_skills =    [   go_skills,
                                        map_skills,
                                        nav_skills,
                                        map_skills,
                                        nav_skills,
                                        move_skills,
                                        move_skills,
                                        trade_skills + buy_skills]

        # Initial task description, should be passed in agent setup
        main_task_description = "Go to store and buy item."

        logger.write(f"Starting {self.name} loop w/ env {config.env_name}")
        logger.write(f"Initial task: {main_task_description}")

        current_state_image = None
        previous_state_image = None

        # Uncomment here if you want to try to make things less undeterministic
        config.set_fixed_seed()

        # Which sub-task to start on, for debugging later steps in the flow
        # But please try to run the whole thing, as the states starting from later are not fully the same
        start_at_step = -1

        use_information_summary = False
        use_gathering_info = False

        # Start interaction loop
        while True:

            if start_at_step >= 0 and start_at_step < len(decomposed_task_steps):

                # Jump configs to later stages...
                sub_task_index = start_at_step
                current_sub_task = decomposed_task_steps[sub_task_index]
                logger.write(f'Starting loop from sub-task #{sub_task_index} - {current_sub_task}')

                # So it doesn't reset in the next loop iteration
                start_at_step = -1

            if current_sub_task is None:
                current_sub_task = decomposed_task_steps[sub_task_index]

            sub_task_description = decomposed_task_description[sub_task_index]
            sub_task_skills = decomposed_task_skills[sub_task_index]
            sub_task_skill_library = self.gm.get_filtered_skills(sub_task_skills)

            self.memory.add_recent_history("task_description", sub_task_description)
            self.memory.add_recent_history("skill_library", sub_task_skill_library)

            logger.write(f"Current sub-task: {current_sub_task}")

            # Stop if limit is reached
            loop_count += 1
            if (config.continuous_mode and 
                config.continuous_limit > 0 and
                loop_count > config.continuous_limit
            ):
                logger.warn(f"Continuous Limit Reached: {config.continuous_limit} iteractions")
                break

            logger.write(f"Loop iteration #{loop_count:0>3}")

            # Get environment input
            logger.write(f"> Capturing screen - state")
            current_state_image, _ = self.gm.capture_screen()
            self.memory.add_recent_history("image", current_state_image)

            self.pause_if_needed(last_executed_skill) # Decide to press pause or not based on skill

            info_response = ""

            # Prepare info gathering, not all steps use it
            if use_gathering_info:
                # Gets the appropriate gathering information prompt inputs for the current sub-task    
                args_func = sub_task_args["gathering_info"]

                logger.write(f'> Gathering information call...')
                data = self.planner.gather_information(input=args_func(current_state_image))
                info_response = data["res_dict"]["description"]

            logger.write(f'R: Description: {info_response}')
            current_context = info_response

            # Prepare decision making
            skills_to_execute = []

            logger.write(f'> Decision making call...')

            data = self.planner.decision_making(input=decision_making_args(self.planner, self.memory))
            skills_to_execute = data['outcome']

            plan_reasoning = data['res_dict']['reasoning']

            if skills_to_execute is None:
                skills_to_execute = []

            logger.write(f'R: Skills: {skills_to_execute}')
            logger.write(f'R: Reasoning: {plan_reasoning}')

            # Action should use the output from the decision making response
            # skill_steps = ['turn(theta=30)', 'move_forward(duration=1)', 'turn(theta=90)', 'move_forward(duration=3)']

            skill_steps = skills_to_execute[:1] # Max steps to execute at once
                
            logger.write(f'> Executing actions in game...')
            logger.write(f'E: Skill Steps: {skill_steps}')
            exec_info = self.gm.execute_actions(skill_steps)

            tmp = exec_info["last_skill"] # exec_info also has the list of successfully executed skills. skill_steps is the full list, which may differ if there were execution errors.
            if tmp is not None and len(tmp) > 0:
                last_executed_skill = tmp 

            logger.write(f"> Capturing screen - post actions. Last: {last_executed_skill}")

            self.memory.add_recent_history("action", last_executed_skill)
            self.memory.add_recent_history("decision_making_reasoning", plan_reasoning)

            current_state_image, _ = self.gm.capture_screen(include_minimap=False)
            self.memory.add_recent_history("image", current_state_image)
            self.pause_if_needed(last_executed_skill) # Decide to press pause or not based on skill

            # summarization starts
            if use_information_summary:
                #self.memory.add_recent_history('image', current_state_image)
                if len(self.memory.get_recent_history("image", self.memory.max_recent_steps)) == 5:
                    args_func = sub_task_args["information_summary"]
                    logger.write(f'> Information summary call...')
                    introductions = ['the first image is the first screenshot of recent events',
                                    'the second image is the second screenshot of recent events',
                                    'the third image is the third screenshot of recent events',
                                    'the fourth image is the fourth screenshot of recent events',
                                    'the fifth image is the fifth screenshot of recent events'] #todo: adding more descriptions
                    data = self.planner.information_summary(input=args_func(self.memory.get_hidden_state(),self.memory.get_image_history(),introductions))
                    info_summary = data['outcome']
                    logger.write(f'R: Summary: {info_summary}')
                    self.memory.add_hidden_state(info_summary)
            # summarization ends

            # Prepare success detection

            logger.write(f'> Success detection call...')
            data = self.planner.success_detection(input=success_detection_args(self.planner, self.memory))

            # Check success
            success = data['outcome']
            success_reasoning = data['res_dict']['reasoning']
            success_criteria = data['res_dict']['criteria']

            self.memory.add_recent_history("success_detection_reasoning", success_reasoning)

            logger.write(f'R: Success: {success}')
            logger.write(f'R: Success criteria: {success_criteria}')
            logger.write(f'R: Success reason: {success_reasoning}')

            # @TODO represent new state for next loop
            if success:
                self.gm.exit_back_to_pause()
                logger.write(f'Finished sub-task: {current_sub_task}')
                sub_task_index += 1

                if sub_task_index >= len(decomposed_task_steps):
                    logger.write(f'Finished task: {main_task_description}!!!')
                    break
                else:
                    # Move to the next subtask with the appropriate configs
                    current_sub_task = decomposed_task_steps[sub_task_index]
                    logger.write(f'New sub-task: {current_sub_task}')

            # @TODO re-use post-action image for info gathering?

            logger.write() #end of loop


    def pause_if_needed(self, last_executed_skill: str):
        paused_skills = trade_skills + buy_skills + map_skills 
        to_remove = ["close_map", "cancel_shopkeeper_interaction"]
        for e in to_remove:
            paused_skills.remove(e)

        if last_executed_skill not in paused_skills:
            logger.warn(f"!! Pausing after skill: {last_executed_skill} !!")
            self.gm.pause_game()
        else:
            logger.warn(f"!! Skipping pause for skill: {last_executed_skill} !!")