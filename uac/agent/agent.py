from typing import List
import json
import time

from uac.config import Config
from uac.log import Logger
from uac.utils.file_utils import assemble_project_path, read_resource_file
from uac.utils.json_utils import load_json
from uac.gameio import GameManager
from uac.planner.planner import Planner
from uac.gameio.atomic_skills.map import __all__ as map_skills
from uac.gameio.atomic_skills.buy import __all__ as buy_skills
from uac.gameio.atomic_skills.trade_utils import __all__ as trade_skills
from uac.gameio.atomic_skills.move import __all__ as move_skills
from uac.gameio.composite_skills.navigation import __all__ as nav_skills
from uac.gameio.composite_skills.go_to_icon import __all__ as go_skills

config = Config()
logger = Logger()


find_horse_params = {
    "__check_list__": [
        "gather_information",
    ],
    "prompt_paths": {
        "inputs": {
            "decision_making": "./res/prompts/inputs/decision_making_find_horse.json",
            "gather_information": "./res/prompts/inputs/gather_information.json",
            "success_detection": "./res/prompts/inputs/success_detection_find_horse.json",
            "information_summary": "./res/prompts/inputs/information_summary.json"
        },
        "templates": {
            "decision_making": "./res/prompts/templates/decision_making_find_horse.prompt",
            "gather_information": "./res/prompts/templates/gather_information.prompt",
            "success_detection": "./res/prompts/templates/success_detection_find_horse.prompt",
            "information_summary": "./res/prompts/templates/information_summary.prompt"
        },
    }
}

create_waypoint_params = {
    "__check_list__": [
        "decision_making",
        "gather_information",
        "success_detection",
        "information_summary"
    ],
    "prompt_paths": {
        "inputs": {
            "decision_making": "./res/prompts/inputs/decision_making_map_create_waypoint.json",
            "gather_information": "./res/prompts/inputs/gather_information.json",
            "success_detection": "./res/prompts/inputs/success_detection_map_create_waypoint.json",
            "information_summary": "./res/prompts/inputs/information_summary.json"
        },
        "templates": {
            "decision_making": "./res/prompts/templates/decision_making_map_create_waypoint.prompt",
            "gather_information": "./res/prompts/templates/gather_information.prompt",
            "success_detection": "./res/prompts/templates/success_detection_map_create_waypoint.prompt",
            "information_summary": "./res/prompts/templates/information_summary.prompt"
        },
    }
}

follow_path_params = {
    "__check_list__": [
        "gather_information",
    ],
    "prompt_paths": {
        "inputs": {
            "decision_making": "./res/prompts/inputs/decision_making_follow_path.json",
            "gather_information": "./res/prompts/inputs/gather_information_follow_path.json",
            "success_detection": "./res/prompts/inputs/success_detection_follow_path.json",
            "information_summary": "./res/prompts/inputs/information_summary.json"
        },
        "templates": {
            "decision_making": "./res/prompts/templates/decision_making_follow_path.prompt",
            "gather_information": "./res/prompts/templates/gather_information_follow_path.prompt",
            "success_detection": "./res/prompts/templates/success_detection_follow_path.prompt",
            "information_summary": "./res/prompts/templates/information_summary.prompt"
        },
    }
}


enter_store_params = {
    "__check_list__": [
        "decision_making",
        "gather_information",
        "success_detection",
        "information_summary"
    ],
    "prompt_paths": {
        "inputs": {
            "decision_making": "./res/prompts/inputs/decision_making_enter_store.json",
            "gather_information": "./res/prompts/inputs/gather_information.json",
            "success_detection": "./res/prompts/inputs/success_detection_enter_store.json",
            "information_summary": "./res/prompts/inputs/information_summary.json"
        },
        "templates": {
            "decision_making": "./res/prompts/templates/decision_making_enter_store.prompt",
            "gather_information": "./res/prompts/templates/gather_information.prompt",
            "success_detection": "./res/prompts/templates/success_detection_enter_store.prompt",
            "information_summary": "./res/prompts/templates/information_summary.prompt"
        },
    }
}

approach_shopkeeper_params = {
    "__check_list__": [
        "decision_making",
        "gather_information",
        "success_detection",
        "information_summary"
    ],
    "prompt_paths": {
        "inputs": {
            "decision_making": "./res/prompts/inputs/decision_making_get_close_to_shopkeeper.json",
            "gather_information": "./res/prompts/inputs/gather_information.json",
            "success_detection": "./res/prompts/inputs/success_detection_get_close_to_shopkeeper.json",
            "information_summary": "./res/prompts/inputs/information_summary.json"
        },
        "templates": {
            "decision_making": "./res/prompts/templates/decision_making_get_close_to_shopkeeper.prompt",
            "gather_information": "./res/prompts/templates/gather_information.prompt",
            "success_detection": "./res/prompts/templates/success_detection_get_close_to_shopkeeper.prompt",
            "information_summary": "./res/prompts/templates/information_summary.prompt"
        },
    }
}


buy_item_params = {
    "__check_list__": [
        "decision_making",
        "gather_information",
        "success_detection",
        "information_summary"
    ],
    "prompt_paths": {
        "inputs": {
            "decision_making": "./res/prompts/inputs/decision_making_buy_item.json",
            "gather_information": "./res/prompts/inputs/gather_information.json",
            "success_detection": "./res/prompts/inputs/success_detection_buy_item.json",
            "information_summary": "./res/prompts/inputs/information_summary.json"
        },
        "templates": {
            "decision_making": "./res/prompts/templates/decision_making_buy_item.prompt",
            "gather_information": "./res/prompts/templates/gather_information.prompt",
            "success_detection": "./res/prompts/templates/success_detection_buy_item.prompt",
            "information_summary": "./res/prompts/templates/information_summary.prompt"
        },
    }
}


def gather_info_args(state_image):
    images_info = [
        {
            "introduction": "This is a screenshot of the current moment in the game",
            "path": state_image,
            "assistant": ""
        }
    ]
    image_introduction = images_info

    output_format = load_json(assemble_project_path("./res/prompts/inputs/gather_information.json"))["output_format"]
    args = {"output_format": output_format, "image_introduction": image_introduction}
    return args

def decision_args(previous_state_image, current_state_image, current_sub_task, current_context, last_executed_skill, last_reasoning, planner):

    previous_actions = []
    if last_executed_skill is not None and len(last_executed_skill) > 0:
        previous_actions = f'[{last_executed_skill}]'

    skillset = go_skills + nav_skills + move_skills 
    skill_library = GameManager(config.env_name).get_filtered_skills(skillset)

    output_format = load_json(assemble_project_path("./res/prompts/inputs/decision_making.json"))["output_format"]

    images_info = [
        {
            "introduction": "This is a screenshot of the current moment in the game",
            "path": current_state_image,
            "assistant": ""
        }
    ]
    image_introduction = images_info

    args = {"context" : current_context, "task_description" : current_sub_task, "skill_library" : skill_library, "previous_actions" : previous_actions, "output_format" : output_format, "image_introduction": image_introduction}
    return args

def suc_det_args(previous_state_image, current_state_image, current_sub_task, plan_reasoning, last_executed_skill, last_reasoning, planner):
            
    output_format = load_json(assemble_project_path("./res/prompts/inputs/success_detection.json"))["output_format"]

    images_info = [
        {
            "introduction": "This is a screenshot of the previous moment in the game",
            "path": previous_state_image,
            "assistant": ""
        },
        {
            "introduction": "This screenshot is the current observation after actions have been executed",
            "path": current_state_image,
            "assistant": ""
        }
    ]
    image_introduction = images_info

    args = {"task_description" : current_sub_task, "current_sub_task" : plan_reasoning, "last_executed_skills" : last_executed_skill, "previous_action" : last_executed_skill, "previous_reasoning" : last_reasoning, "output_format" : output_format, "image_introduction": image_introduction}
    return args

def info_sum_args(hidden_state, images, introductions):

    output_format = load_json(assemble_project_path("./res/prompts/inputs/information_summary.json"))["output_format"]

    images_info = [
        {
            "introduction": introductions[0],
            "path": images[0],
            "assistant": ""
        },
        {
            "introduction": introductions[1],
            "path": images[1],
            "assistant": ""
        },
        {
            "introduction": introductions[2],
            "path": images[2],
            "assistant": ""
        },
        {
            "introduction": introductions[3],
            "path": images[3],
            "assistant": ""
        },
        {
            "introduction": introductions[4],
            "path": images[4],
            "assistant": ""
        }
    ]
    image_introduction = images_info

    args = {"hidden_state" : hidden_state, "output_format" : output_format, "image_introduction": image_introduction}
    return args

def cw_decision_args(previous_state_image, current_state_image, current_sub_task, current_context, last_executed_skill, last_reasoning, planner):

    if previous_state_image is None:
        previous_state_image = current_state_image

    input = planner.decision_making_.input_map

    target = current_sub_task.split()[-1] # last word

    input["task_description"] = f'Mark the "{target}" on a Map as the Waypoint via the Index and close the Map to return to the gameplay.'

    number_of_execute_skills = input["number_of_execute_skills"]

    input["previous_action"] = last_executed_skill
    input["previous_reasoning"] = last_reasoning

    input['skill_library'] = GameManager(config.env_name).get_filtered_skills(map_skills)

    image_introduction = [
        {
            "introduction": input["image_introduction"][-2]["introduction"],
            "path": previous_state_image,
            "assistant": input["image_introduction"][-2]["assistant"]
        },
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": current_state_image,
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]

    input["image_introduction"] = image_introduction
    return input

def cw_suc_det_args(previous_state_image, current_state_image, current_sub_task, plan_reasoning, last_executed_skill, last_reasoning, planner):
        
    input = planner.success_detection_.input_map

    target = current_sub_task.split()[-1] # last word

    input["task_description"] = f'Mark the "{target}" on a Map as the Waypoint via the Index.'
    
    image_introduction = [
        {
            "introduction": input["image_introduction"][-2]["introduction"],
            "path": previous_state_image,
            "assistant": input["image_introduction"][-2]["assistant"]
        },
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": current_state_image,
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]
    input["image_introduction"] = image_introduction
    input["previous_action"] = last_executed_skill
    input["previous_reasoning"] = last_reasoning
    return input

def enter_decision_args(previous_state_image, current_state_image, current_sub_task, current_context, last_executed_skill, last_reasoning, planner):

    if previous_state_image is None:
        previous_state_image = current_state_image

    input = planner.decision_making_.input_map

    number_of_execute_skills = input["number_of_execute_skills"]

    if last_executed_skill:
        input["previous_action"] = last_executed_skill
        input["previous_reasoning"] = last_reasoning

    input['skill_library'] = GameManager(config.env_name).get_filtered_skills(move_skills)

    image_introduction = [
        {
            "introduction": input["image_introduction"][-2]["introduction"],
            "path": previous_state_image,
            "assistant": input["image_introduction"][-2]["assistant"]
        },
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": current_state_image,
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]

    input["image_introduction"] = image_introduction
    return input

def enter_suc_det_args(previous_state_image, current_state_image, current_sub_task, plan_reasoning, last_executed_skill, last_reasoning, planner):
        
    input = planner.success_detection_.input_map
    image_introduction = [
        {
            "introduction": input["image_introduction"][-2]["introduction"],
            "path": previous_state_image,
            "assistant": input["image_introduction"][-2]["assistant"]
        },
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": current_state_image,
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]
    input["image_introduction"] = image_introduction
    input["previous_action"] = last_executed_skill
    input["previous_reasoning"] = last_reasoning
    return input

def buy_decision_args(previous_state_image, current_state_image, current_sub_task, current_context, last_executed_skill, last_reasoning, planner):

    if previous_state_image is None:
        previous_state_image = current_state_image

    input = planner.decision_making_.input_map

    number_of_execute_skills = input["number_of_execute_skills"]

    if last_executed_skill:
        input["previous_action"] = last_executed_skill
        input["previous_reasoning"] = last_reasoning

    input['skill_library'] = GameManager(config.env_name).get_filtered_skills(trade_skills + buy_skills)

    image_introduction = [
        {
            "introduction": input["image_introduction"][-2]["introduction"],
            "path": previous_state_image,
            "assistant": input["image_introduction"][-2]["assistant"]
        },
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": current_state_image,
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]

    input["image_introduction"] = image_introduction
    return input

def buy_suc_det_args(previous_state_image, current_state_image, current_sub_task, plan_reasoning, last_executed_skill, last_reasoning, planner):
        
    input = planner.success_detection_.input_map
    image_introduction = [
        {
            "introduction": input["image_introduction"][-2]["introduction"],
            "path": previous_state_image,
            "assistant": input["image_introduction"][-2]["assistant"]
        },
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": current_state_image,
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]
    input["image_introduction"] = image_introduction
    input["previous_action"] = last_executed_skill
    input["previous_reasoning"] = last_reasoning
    return input


find_horse_args = dict()
find_horse_args['gathering_info'] = gather_info_args
find_horse_args['decision_making'] = decision_args
find_horse_args['success_detection'] = suc_det_args
find_horse_args['information_summary'] = info_sum_args

create_waypoint_args = dict()
create_waypoint_args['gathering_info'] = None
create_waypoint_args['decision_making'] = cw_decision_args
create_waypoint_args['success_detection'] = cw_suc_det_args
find_horse_args['information_summary'] = info_sum_args

frl_args = dict()
frl_args['gathering_info'] = gather_info_args
frl_args['decision_making'] = decision_args
frl_args['success_detection'] = suc_det_args
find_horse_args['information_summary'] = info_sum_args

enter_args = dict()
enter_args['gathering_info'] = None
enter_args['decision_making'] = enter_decision_args
enter_args['success_detection'] = enter_suc_det_args
find_horse_args['information_summary'] = info_sum_args

buy_args = dict()
buy_args['gathering_info'] = None
buy_args['decision_making'] = buy_decision_args
buy_args['success_detection'] = buy_suc_det_args
find_horse_args['information_summary'] = info_sum_args

approach_shopkeeper_args = dict()
approach_shopkeeper_args['gathering_info'] = None
approach_shopkeeper_args['decision_making'] = enter_decision_args
approach_shopkeeper_args['success_detection'] = enter_suc_det_args
find_horse_args['information_summary'] = info_sum_args

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
        
        config.continuous_limit = 10

        # Interaction Loop
        loop_count = 0

        last_executed_skill = None

        plan_reasoning = ""
        last_reasoning = ""

        previous_sub_task = None
        
        current_sub_task = None
        sub_task_args = None
        sub_task_params = None
        
        sub_task_index = 0

        previous_context = None
        current_context = None

        # @TODO HACK 
        decomposed_task_steps          = ["Go to the horse and mount it", "Create waypoint to the saloon", "Follow the red line to the saloon", "Create waypoint to the store", "Follow the red line to the store", "Enter the store",  "Approach shopkeeper",      "Buy apple"]
        decomposed_task_planner_params = [find_horse_params,              create_waypoint_params,          follow_path_params,                  create_waypoint_params,         follow_path_params,                 enter_store_params, approach_shopkeeper_params, buy_item_params]
        decomposed_task_args           = [find_horse_args,                create_waypoint_args,            frl_args,                            create_waypoint_args,           frl_args,                           enter_args,         approach_shopkeeper_args,   buy_args]

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

        # Start interaction loop
        while True:

            if start_at_step >= 0 and start_at_step < len(decomposed_task_steps):

                # Jump configs to later stages...
                sub_task_index = start_at_step
                current_sub_task = decomposed_task_steps[sub_task_index]
                logger.write(f'Starting loop from sub-task #{sub_task_index} - {current_sub_task}')
                
                sub_task_params = decomposed_task_planner_params[sub_task_index]
                self.planner.set_internal_params(sub_task_params, use_information_summary = use_information_summary)
                sub_task_args = decomposed_task_args[sub_task_index]

                # So it doesn't reset in the next loop iteration
                start_at_step = -1

            if current_sub_task is None:
                current_sub_task = decomposed_task_steps[sub_task_index]
                sub_task_params = decomposed_task_planner_params[sub_task_index]
                sub_task_args = decomposed_task_args[sub_task_index]

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
            current_state_image, _ = self.env_manager.capture_screen()
            self.pause_if_needed(last_executed_skill) # Decide to press pause or not based on skill

            info_response = ""

            # Prepare info gathering, not all steps use it
            if sub_task_args["gathering_info"] is not None:

                # Gets the appropriate gathering information prompt inputs for the current sub-task    
                args_func = sub_task_args["gathering_info"]

                logger.write(f'> Gathering information call...')
                data = self.planner.gather_information(input=args_func(current_state_image))
                info_response = data["res_dict"]["description"]

            logger.write(f'R: Description: {info_response}')
            current_context = info_response

            # Prepare decision making
            skills_to_execute = []

            # Context should use the description from the gather_information response, if relevant
            if current_context is not None:
                previous_context = current_context

            # Gets the appropriate decision making prompt inputs for the current sub-task
            args_func = sub_task_args["decision_making"]

            logger.write(f'> Decision making call...')
            data = self.planner.decision_making(input=args_func(previous_state_image, current_state_image, current_sub_task, current_context, last_executed_skill, last_reasoning, self.planner))
            skills_to_execute = data['outcome']

            last_reasoning = plan_reasoning
            plan_reasoning = data['res_dict']['reasoning']

            if skills_to_execute is None:
                skills_to_execute = []

            logger.write(f'R: Skills: {skills_to_execute}')
            logger.write(f'R: Reasoning: {plan_reasoning}')

            # Action should use the output from the decision making response
            # skill_steps = ['turn(theta=30)', 'move_forward(duration=1)', 'turn(theta=90)', 'move_forward(duration=3)']

            if decomposed_task_steps[sub_task_index] in ["Enter the store",  "Approach shopkeeper"]: 
                skill_steps = skills_to_execute[:2] # Max steps to execute at once
            else:
                skill_steps = skills_to_execute[:1] # Max steps to execute at once
                
            logger.write(f'> Executing actions in game...')
            logger.write(f'E: Skill Steps: {skill_steps}')
            exec_info = self.env_manager.execute_actions(skill_steps)

            tmp = exec_info["last_skill"] # exec_info also has the list of successfully executed skills. skill_steps is the full list, which may differ if there were execution errors.
            if tmp is not None and len(tmp) > 0:
                last_executed_skill = tmp 

            logger.write(f"> Capturing screen - post actions. Last: {last_executed_skill}")
            previous_state_image = current_state_image
            current_state_image, _ = self.env_manager.capture_screen(include_minimap=False)
            self.pause_if_needed(last_executed_skill) # Decide to press pause or not based on skill

            # summarization starts
            if use_information_summary:
                self.memory.add_recent_history('image', current_state_image)
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
                    logger.write(f'R: Rummary: {info_summary}')
                    self.memory.add_hidden_state(info_summary)
            # summarization ends

            # Prepare success detection

            # Gets the appropriate success detection prompt inputs for the current sub-task
            args_func = sub_task_args["success_detection"]

            logger.write(f'> Success detection call...')
            data = self.planner.success_detection(input=args_func(previous_state_image, current_state_image, current_sub_task, plan_reasoning, last_executed_skill, last_reasoning, self.planner))

            # Check success
            res_dict = data['res_dict']
            reasoning = res_dict['decision']['reasoning']
            success = data['outcome']

            logger.write(f'R: Success: {success}')
            logger.write(f'R: Reasoning: {reasoning}')

            # @TODO represent new state for next loop
            if success:
                logger.write(f'Finished sub-task: {current_sub_task}')
                previous_sub_task = current_sub_task
                sub_task_index += 1
                plan_reasoning = ""
                last_reasoning = ""

                if sub_task_index >= len(decomposed_task_steps):
                    logger.write(f'Finished task: {main_task_description}!!!')
                    break
                else:

                    # Move to the next subtask with the appropriate configs
                    current_sub_task = decomposed_task_steps[sub_task_index]
                    logger.write(f'New sub-task: {current_sub_task}')

                    # Set planner param and necessary arguments            
                    sub_task_params = decomposed_task_planner_params[sub_task_index]
                    self.planner.set_internal_params(sub_task_params)
                    sub_task_args = decomposed_task_args[sub_task_index]

            # @TODO re-use post-action image for info gathering?

            logger.write() #end of loop


    def pause_if_needed(self, last_executed_skill: str):
        paused_skills = trade_skills + buy_skills + map_skills 
        to_remove = ["close_map", "cancel_shopkeeper_interaction"]
        for e in to_remove:
            paused_skills.remove(e)

        if last_executed_skill not in paused_skills:
            logger.warn(f"!! Pausing after skill: {last_executed_skill} !!")
            self.env_manager.pause_game()
        else:
            logger.warn(f"!! Skipping pause for skill: {last_executed_skill} !!")