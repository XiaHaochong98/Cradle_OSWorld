import os
import time

from uac.config import Config
from uac.gameio.game_manager import GameManager
from uac.log import Logger
from uac.agent import Agent
from uac.planner.base import to_text
from uac.planner.planner import Planner
from uac.provider.openai import OpenAIProvider
from uac.gameio.lifecycle.ui_control import switch_to_game, pause_game, unpause_game
from uac.gameio.atomic_skills.move import __all__ as move_skills
from uac.utils.file_utils import read_resource_file
import pydirectinput

config = Config()
logger = Logger()

def main_test_decision_making():
    planner_params = {
        "__check_list__": [
            "decision_making",
            "gather_information",
            "success_detection"
        ],
        "prompt_paths": {
            "input_example": {
                "decision_making": "./res/prompts/template_input/decision_making_enter_store.json",
                "gather_information": "./res/prompts/template_input/gather_information.json",
                "success_detection": "./res/prompts/template_input/success_detection.json"

            },
            "templates": {
                "decision_making": "./res/prompts/templates/decision_making_enter_store.prompt",
                "gather_information": "./res/prompts/templates/gather_information.prompt",
                "success_detection": "./res/prompts/templates/success_detection.prompt"
            },
            "output_example": {
                "decision_making": "./res/prompts/api_output/decision_making_enter_store.json",
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
    input = planner.decision_making_.input_map

    gm = GameManager(config.env_name)

    skill_library = gm.get_filtered_skills(move_skills)

    image_introduction = [
        # {
        #     "introduction": "Here are some examples of trading in the game.",
        #     "path": "",
        #     "assistant": ""
        # },
        # {
        #     "introduction": "This example shows that the CARROT is currently selected in the image.",
        #     "path": r"C:\Users\28094\Desktop\UAC_wentao_1124_1127\UAC\runs\1701163597.4037797\screen_1701163732.2476993.jpg",
        #     "assistant": "Yes. That is correct!"
        # },
        # {
        #     "introduction": "This example shows that the Canned SALMON is currently selected in the image.",
        #     "path": r"C:\Users\28094\Desktop\UAC_wentao_1124_1127\UAC\runs\1701163597.4037797\screen_1701163680.5057523.jpg",
        #     "assistant": "Yes. That is correct!"
        # },
        # {
        #     "introduction": "I will give you two images for decision making.",
        #     "path": "",
        #     "assistant": ""
        # },
        {
            "introduction": input["image_introduction"][-2]["introduction"],
            "path": "res/prompts/testing/decision_making/buy/4.jpg",
            "assistant": input["image_introduction"][-2]["assistant"]
        },
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": "res/prompts/testing/decision_making/buy/5.jpg",
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]
    input["image_introduction"] = image_introduction
    input['skill_library'] = skill_library
    input["previous_action"] = "view_next_page()"
    input["previous_reasoning"] = "The current page displayed is the 'Canned Food' section of the Wheeler, Rawson & Co. catalogue, which includes a variety of canned goods. Items on the page, from the top left and moving to the right, are: Big Valley Canned Apricots, Schmitz Baked Beans, Flock of Sparrows Canned Kidney Beans, Big Valley Canned Peaches, Edna McSweeney Brand Canned Corned Beef, Blackwing Foods Canned Sweetcorn, Dewberry Brand Canned Peas, and Big Valley Canned Pineapples. The currently selected item is 'Canned Apricots' as indicated by the box around the item's description at the bottom of the screen. The target item, which is an 'Apple,' is not depicted on the current screen as these are all canned goods and do not include fresh produce. Therefore, the next logical step would be to navigate to the next page, which likely contains the Fresh Food section, with the hope of finding an apple there."
    data = planner.decision_making(input = input)

    skill_steps = data['outcome']
    if skill_steps is None:
        skill_steps = []

    logger.write(f'Skill Steps: {skill_steps}')
    pre_reasoning = ''
    if 'res_dict' in data.keys() and 'reason' in data['res_dict'].keys():
        pre_reasoning = data['res_dict']['reason']

    # For such cases with no expected response, we should define a retry limit
    logger.write(f'Decision reason: {pre_reasoning}')

def main_test_success_detection():

    planner_params = {
        "__check_list__": [
            "decision_making",
            "gather_information",
            "success_detection"
        ],
        "prompt_paths": {
            "input_example": {
                "decision_making": "./res/prompts/template_input/decision_making_enter_store.json",
                "gather_information": "./res/prompts/template_input/gather_information.json",
                "success_detection": "./res/prompts/template_input/success_detection_enter_store.json"
            },
            "templates": {
                "decision_making": "./res/prompts/templates/decision_making_enter_store.prompt",
                "gather_information": "./res/prompts/templates/gather_information.prompt",
                "success_detection": "./res/prompts/templates/success_detection_enter_store.prompt"
            },
            "output_example": {
                "decision_making": "./res/prompts/api_output/decision_making_enter_store.json",
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
            "path": "res/prompts/testing/success_detection/enter_store/2.jpg",
            "assistant": input["image_introduction"][-2]["assistant"]
        },
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": "res/prompts/testing/success_detection/enter_store/3.jpg",
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]
    input["image_introduction"] = image_introduction



    # 0/1.jpg 
    # pre_skill = 'move_forward(duration=1)'
    # pre_reasoning = "Looking at the current screenshot, the door to the general store is still directly in front of the character, and it does not appear that the character has deviated from the path towards the door. The previous action to move forward for a duration of 1 second was appropriate, and no corrections in the form of a turn seem to be required. There are no visible obstacles such as hitching posts, people, or horses directly in front of the character that would impede movement towards the door of the general store. Therefore, the character should continue to move forward for another second to reach the door. The previous reasoning for the last action still applies and appears to be correct as there's nothing in the current screenshot to contradict it or suggest a need for a different action."

    # 1/2.jpg 
    # pre_skill = 'move_forward(duration=1)'
    # pre_reasoning = "In the current screenshot, the character has moved closer to the door of the general store, indicating that the previous action of moving forward was correct. There are no visible obstacles directly in front of the character that would prevent entry into the store. The door to the general store is right in front of the character and no additional turning is required to face it. The character seems well aligned with the door, thus no turn function is needed at this moment. The next reasonable action is to continue moving forward to enter the general store. Since the duration parameter for moving forward should be exactly 1 second, we will proceed with that."

    # 2/3.jpg 
    pre_skill = ''
    pre_reasoning = "In the current screenshot, the character has successfully entered the general store, which was the given task. There is no need for further movement or turning since the character is already inside the store, facing the shopkeeper, and properly aligned to interact. Hence, no action is required at this precise moment. The last executed action of moving forward for 1 second seems to have been appropriate as it resulted in the character positioning himself just inside the store without any obstacles in the immediate vicinity. There is no inconsistency with the current screenshot; the previous reasoning was correct, and the task to enter the general store has been completed."

    input["previous_action"] = pre_skill
    input["previous_reasoning"] = pre_reasoning

    data = planner.success_detection(input = input)

    res_dict = data['res_dict']['decision']
    reason = res_dict['reason']
    success = data['outcome']

    logger.write(f'Success: {success}')
    logger.write(f'Reason: {reason}')


def main_pipeline():
    planner_params = {
        "__check_list__": [
            "decision_making",
            "gather_information",
            "success_detection"
        ],
        "prompt_paths": {
            "input_example": {
                "decision_making": "./res/prompts/template_input/decision_making_enter_store.json",
                "gather_information": "./res/prompts/template_input/gather_information.json",
                "success_detection": "./res/prompts/template_input/success_detection_enter_store.json"

            },
            "templates": {
                "decision_making": "./res/prompts/templates/decision_making_enter_store.prompt",
                "gather_information": "./res/prompts/templates/gather_information.prompt",
                "success_detection": "./res/prompts/templates/success_detection_enter_store.prompt"
            },
            "output_example": {
                "decision_making": "./res/prompts/api_output/decision_making_enter_store.json",
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

    skill_library = gm.get_filtered_skills(move_skills)

    switch_to_game()

    pre_screen_shot_path, _ = gm.capture_screen()
    cur_screen_shot_path = pre_screen_shot_path
    success = False
    pre_skill = ""
    pre_reasoning = ""
    pause_game()

    while not success:
        # for decision making
        input = planner.decision_making_.input_map

        number_of_execute_skills = input["number_of_execute_skills"]

        if pre_skill:
            input["previous_action"] = pre_skill
            input["previous_reasoning"] = pre_reasoning

        input['skill_library'] = skill_library


        image_introduction = [
            # {
            #     "introduction": "Here are some examples of trading in the game.",
            #     "path": "",
            #     "assistant": ""
            # },
            # {
            #     "introduction": "This example shows that the CARROT is currently selected in the image.",
            #     "path": r"C:\Users\28094\Desktop\UAC_wentao_1124_1127\UAC\runs\1701163597.4037797\screen_1701163732.2476993.jpg",
            #     "assistant": "Yes. That is correct!"
            # },
            # {
            #     "introduction": "This example shows that the Canned SALMON is currently selected in the image.",
            #     "path": r"C:\Users\28094\Desktop\UAC_wentao_1124_1127\UAC\runs\1701163597.4037797\screen_1701163680.5057523.jpg",
            #     "assistant": "Yes. That is correct!"
            # },
            # {
            #     "introduction": "I will give you two images for decision making.",
            #     "path": "",
            #     "assistant": ""
            # },
            # {
            #     "introduction": "This image is the front scene of the general store for reference.",
            #     "path": r"C:\Users\28094\Desktop\UAC_main_1129\UAC\res\prompts\testing\decision_making\enter_store\screen_1701265459.72348.jpg",
            #     "assistant": ""
            # },
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

        data = planner.decision_making(input = input)

        skill_steps = data['outcome']
        if skill_steps is None:
            skill_steps = []

        logger.write(f'R: {skill_steps}')

        skill_steps = skill_steps[:number_of_execute_skills]
        logger.write(f'Skill Steps: {skill_steps}')

        unpause_game()
        exec_info = gm.execute_actions(skill_steps)

        #pre_skill = exec_info[1]
        pre_skill = skill_steps

        pre_reasoning = ''
        if 'res_dict' in data.keys() and 'reason' in data['res_dict'].keys():
            pre_reasoning = data['res_dict']['reason']

        # For such cases with no expected response, we should define a retry limit

        #logger.write(f'Decision reason: {pre_reasoning}')
        #pre_reasoning = data['res_dict']['reason']
        logger.write(f'Decision reason: {pre_reasoning}')

        pre_screen_shot_path = cur_screen_shot_path
        cur_screen_shot_path, _ = gm.capture_screen()

        pause_game()

        # for success detection
        input = planner.success_detection_.input_map
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
        input["previous_action"] = pre_skill
        input["previous_reasoning"] = pre_reasoning

        data = planner.success_detection(input = input)

        success = data['outcome']
        success_reason = data['res_dict']['decision']['reason']
        logger.write(f'Success: {success}')
        logger.write(f'Success reason: {success_reason}')

if __name__ == '__main__':

    config.set_fixed_seed()

    # not implemented
    # main_test_decision_making()

    #main_test_success_detection()

    main_pipeline()