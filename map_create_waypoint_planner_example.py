import os
import time

from uac.config import Config
from uac.gameio.game_manager import GameManager
from uac.log import Logger
from uac.agent import Agent
from uac.planner.base import to_text
from uac.planner.planner import Planner
from uac.provider.openai import OpenAIProvider
from uac.gameio.lifecycle.ui_control import switch_to_game
from uac.gameio.atomic_skills.map import __all__ as map_skills
from uac.utils.file_utils import read_resource_file

config = Config()
logger = Logger()
config.set_fixed_seed()

def main_test_decision_making():
    planner_params = {
        "__check_list__": [
            "decision_making",
            "gather_information",
            "success_detection"
        ],
        "prompt_paths": {
            "input_example": {
                "decision_making": "./res/prompts/template_input/decision_making_map_create_waypoint.json",
                "gather_information": "./res/prompts/template_input/gather_information.json",
                "success_detection": "./res/prompts/template_input/success_detection_map_create_waypoint.json"

            },
            "templates": {
                "decision_making": "./res/prompts/templates/decision_making_map_create_waypoint.prompt",
                "gather_information": "./res/prompts/templates/gather_information.prompt",
                "success_detection": "./res/prompts/templates/success_detection.prompt"
            },
            "output_example": {
                "decision_making": "./res/prompts/api_output/decision_making.json",
                "gather_information": "./res/prompts/api_output/gather_information.json",
                "success_detection": "./res/prompts/api_output/success_detection.json"
            }
        }
    }

    system_prompt_template = read_resource_file("./res/prompts/templates/system.prompt")
    args = {"environment_name" : config.env_name}
    system_prompt = to_text(system_prompt_template, args)

    llm_provider_config_path = './conf/openai_config.json'

    llm_provider = OpenAIProvider()
    llm_provider.init_provider(llm_provider_config_path)
    planner = Planner(llm_provider=llm_provider,
                      system_prompts=[system_prompt],
                      planner_params=planner_params)

    gm = GameManager(config.env_name)
    skill_library = gm.get_filtered_skills(map_skills)

    input = planner.decision_making_.input_map

    input['skill_library'] = skill_library
    input["previous_action"] = "select_next_index_object"
    data = planner.decision_making(input=input)

    res_dict = data['res_dict']
    reasoning = res_dict['reasoning']

    skill_steps = data['outcome']

    logger.write(f'R: {skill_steps}')
    logger.write(f'R: {reasoning}')

    logger.write()


def main_test_success_detection():
    planner_params = {
        "__check_list__": [
            "decision_making",
            "gather_information",
            "success_detection"
        ],
        "prompt_paths": {
            "input_example": {
                "decision_making": "./res/prompts/template_input/decision_making_map_create_waypoint.json",
                "gather_information": "./res/prompts/template_input/gather_information.json",
                "success_detection": "./res/prompts/template_input/success_detection_map_create_waypoint.json"

            },
            "templates": {
                "decision_making": "./res/prompts/templates/decision_making_map_create_waypoint.prompt",
                "gather_information": "./res/prompts/templates/gather_information.prompt",
                "success_detection": "./res/prompts/templates/success_detection_map_create_waypoint.prompt"
            },
            "output_example": {
                "decision_making": "./res/prompts/api_output/decision_making.json",
                "gather_information": "./res/prompts/api_output/gather_information.json",
                "success_detection": "./res/prompts/api_output/success_detection.json"
            }
        }
    }

    system_prompt_template = read_resource_file("./res/prompts/templates/system.prompt")
    args = {"environment_name" : config.env_name}
    system_prompt = to_text(system_prompt_template, args)

    llm_provider_config_path = './conf/openai_config.json'

    llm_provider = OpenAIProvider()
    llm_provider.init_provider(llm_provider_config_path)
    planner = Planner(llm_provider=llm_provider,
                      system_prompts=[system_prompt],
                      planner_params=planner_params)


    input = planner.success_detection_.input_map
    image_introduction = [
        {
            "introduction": input["image_introduction"][-2]["introduction"],
            "path": "./res/prompts/testing/decision_making/map_create_waypoint/screenshots/1.jpg",
            "assistant": input["image_introduction"][-2]["assistant"]
        },
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": "./res/prompts/testing/decision_making/map_create_waypoint/screenshots/2.jpg",
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]
    input["image_introduction"] = image_introduction
    pre_skill = 'add_waypoint()'
    pre_reasoning = "The current task is to mark the 'Saloon' on the map as a waypoint, and as per the last action, the selection has moved down the list but has not found the 'Saloon' yet. The 'Provisions' is currently selected, which suggests that the 'Saloon' might be further down the list. Therefore, the next logical step is to continue navigating down the index using select_down_index_object() until the 'Saloon' option is highlighted, at which point a waypoint can be set."

    input["previous_action"] = pre_skill
    input["previous_reasoning"] = pre_reasoning

    data = planner.success_detection(input = input)

    
    # print("data['res_dict']", data['res_dict']['decision'])
    # print("keys", data['res_dict']['decision'].keys())

    res_dict = data['res_dict']['decision']
    reasoning = res_dict['reasoning']
    success = data['outcome']

    logger.write(f'Success: {success}')
    logger.write(f'Reasoning: {reasoning}')


def main_pipeline():
    planner_params = {
        "__check_list__": [
            "decision_making",
            "gather_information",
            "success_detection"
        ],
        "prompt_paths": {
            "input_example": {
                "decision_making": "./res/prompts/template_input/decision_making_map_create_waypoint.json",
                "gather_information": "./res/prompts/template_input/gather_information.json",
                "success_detection": "./res/prompts/template_input/success_detection_map_create_waypoint.json"
            },
            "templates": {
                "decision_making": "./res/prompts/templates/decision_making_map_create_waypoint.prompt",
                "gather_information": "./res/prompts/templates/gather_information.prompt",
                "success_detection": "./res/prompts/templates/success_detection_map_create_waypoint.prompt"
            },
            "output_example": {
                "decision_making": "./res/prompts/api_output/decision_making.json",
                "gather_information": "./res/prompts/api_output/gather_information.json",
                "success_detection": "./res/prompts/api_output/success_detection.json"
            }
        }
    }

    system_prompt_template = read_resource_file("./res/prompts/templates/system.prompt")
    args = {"environment_name" : config.env_name}
    system_prompt = to_text(system_prompt_template, args)

    llm_provider_config_path = './conf/openai_config.json'

    llm_provider = OpenAIProvider()
    llm_provider.init_provider(llm_provider_config_path)
    planner = Planner(llm_provider=llm_provider,
                      system_prompts=[system_prompt],
                      planner_params=planner_params)

    gm = GameManager(config.env_name)

    skill_library = gm.get_filtered_skills(map_skills)

    pre_screen_shot_path, _ = gm.capture_screen()
    cur_screen_shot_path = pre_screen_shot_path

    success = False
    pre_skill = ''
    pre_reasoning = ''

    while not success:
        # for decision making
        input = planner.decision_making_.input_map

        number_of_execute_skills = input["number_of_execute_skills"]

        input["previous_action"] = pre_skill
        input["previous_reasoning"] = pre_reasoning

        input['skill_library'] = skill_library

        image_introduction = [
            {
                "introduction": input["image_introduction"][-2]["introduction"],
                "path": pre_screen_shot_path,
                "assistant": input["image_introduction"][-2]["assistant"]
            },
            {
                "introduction": input["image_introduction"][-1]["introduction"],
                "path": cur_screen_shot_path,
                "assistant": input["image_introduction"][-1]["assistant"]
            }
        ]
        input["image_introduction"] = image_introduction
        #skill_steps = planner.decision_making(input = input)['']

        # logger.warn(f'Images are: {pre_screen_shot_path}, {cur_screen_shot_path}')

        # logger.write(f'U: {input}')

        data = planner.decision_making(input = input)

        skill_steps = data['outcome']
        if skill_steps is None:
            skill_steps = []

        logger.write(f'R: {skill_steps}')

        skill_steps = skill_steps[:number_of_execute_skills]
        logger.write(f'Skill Steps: {skill_steps}')

        exec_info = gm.execute_actions(skill_steps)

        pre_skill = exec_info["last_skill"] # exec_info also has the list of successfully executed skills. skill_steps is the full list, which may differ if there were execution errors.

        pre_reasoning = ''
        if 'res_dict' in data.keys() and 'reasoning' in data['res_dict'].keys():
            pre_reasoning = data['res_dict']['reasoning']

        # For such cases with no expected response, we should define a retry limit

        logger.write(f'Decision reasoning: {pre_reasoning}')

        pre_screen_shot_path = cur_screen_shot_path
        cur_screen_shot_path, _ = gm.capture_screen()

        # for success detection
        # input = planner.success_detection_.input_map
        # image_introduction = [
        #     {
        #         "introduction": input["image_introduction"][-2]["introduction"],
        #         "path": pre_screen_shot_path,
        #         "assistant": input["image_introduction"][-2]["assistant"]
        #     },
        #     {
        #         "introduction": input["image_introduction"][-1]["introduction"],
        #         "path": cur_screen_shot_path,
        #         "assistant": input["image_introduction"][-1]["assistant"]
        #     }
        # ]
        # input["image_introduction"] = image_introduction
        # input["previous_action"] = pre_skill
        # input["previous_reasoning"] = pre_reasoning

        # data = planner.success_detection(input = input)

        # success = data['outcome']
        # success_reasoning = data['res_dict']['decision']['reasoning']
        # logger.write(f'Success: {success}')
        # logger.write(f'Success reasoning: {success_reasoning}')


if __name__ == '__main__':
    # main_test_decision_making()

    # main_test_success_detection()

    main_pipeline()
