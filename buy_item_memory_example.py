import os
import time

from uac.config import Config
from uac.gameio.game_manager import GameManager
from uac.log import Logger
from uac.agent import Agent
from uac.planner.base import to_text
from uac.planner.planner import Planner
from uac.memory.interface import MemoryInterface
from uac.provider.openai import OpenAIProvider
from uac.gameio.lifecycle.ui_control import switch_to_game
from uac.gameio.atomic_skills.trade_utils import __all__ as trade_skills
from uac.gameio.atomic_skills.buy import __all__ as buy_skills
from uac.utils.file_utils import read_resource_file

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
                "decision_making": "./res/prompts/template_input/decision_making_buy_item.json",
                "gather_information": "./res/prompts/template_input/gather_information.json",
                "success_detection": "./res/prompts/template_input/success_detection.json"

            },
            "templates": {
                "decision_making": "./res/prompts/templates/decision_making_buy_item.prompt",
                "gather_information": "./res/prompts/templates/gather_information.prompt",
                "success_detection": "./res/prompts/templates/success_detection.prompt"
            },
            "output_example": {
                "decision_making": "./res/prompts/api_output/decision_making_buy_item.json",
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

    skill_library = gm.get_filtered_skills(trade_skills + buy_skills)

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
    if 'res_dict' in data.keys() and 'reasoning' in data['res_dict'].keys():
        pre_reasoning = data['res_dict']['reasoning']

    # For such cases with no expected response, we should define a retry limit
    logger.write(f'Decision reasoning: {pre_reasoning}')

def main_test_success_detection():

    planner_params = {
        "__check_list__": [
            "decision_making",
            "gather_information",
            "success_detection"
        ],
        "prompt_paths": {
            "input_example": {
                "decision_making": "./res/prompts/template_input/decision_making_buy_item.json",
                "gather_information": "./res/prompts/template_input/gather_information.json",
                "success_detection": "./res/prompts/template_input/success_detection_buy_item.json"
            },
            "templates": {
                "decision_making": "./res/prompts/templates/decision_making_buy_item.prompt",
                "gather_information": "./res/prompts/templates/gather_information.prompt",
                "success_detection": "./res/prompts/templates/success_detection_buy_item.prompt"
            },
            "output_example": {
                "decision_making": "./res/prompts/api_output/decision_making_buy_item.json",
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
            "path": "res/prompts/testing/decision_making/buy/7.jpg",
            "assistant": input["image_introduction"][-2]["assistant"]
        },
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": "res/prompts/testing/decision_making/buy/8.jpg",
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]
    input["image_introduction"] = image_introduction

    pre_skill = 'buy_product()'
    pre_reasoning = "1. The items on the screen from top left moving right are: Big Valley Canned Strawberries, Schmitz Canned Salmon, a warning advertisement, Local Produce Apple, Local Produce Corn, Local Produce Carrot. 2. Yes, the target item 'Apple' is on the current screen, located under the 'Local Produce' section in the top right quadrant. 3. The currently selected item is the Apple, as indicated by the highlighted description at the bottom of the screen which says 'Apple'. Since the target item 'Apple' is selected, the next action is to purchase it."

    input["previous_action"] = pre_skill
    input["previous_reasoning"] = pre_reasoning

    data = planner.success_detection(input = input)

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
                "decision_making": "./res/prompts/template_input/decision_making_buy_item.json",
                "gather_information": "./res/prompts/template_input/gather_information.json",
                "success_detection": "./res/prompts/template_input/success_detection_buy_item.json"

            },
            "templates": {
                "decision_making": "./res/prompts/templates/decision_making_buy_item.prompt",
                "gather_information": "./res/prompts/templates/gather_information.prompt",
                "success_detection": "./res/prompts/templates/success_detection_buy_item.prompt"
            },
            "output_example": {
                "decision_making": "./res/prompts/api_output/decision_making_buy_item.json",
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
    memory = MemoryInterface(
        memory_path='./res/memory',
        vectorstores={},
        embedding_provider=llm_provider
    )

    gm = GameManager(config.env_name)

    skill_library = gm.get_filtered_skills(trade_skills + buy_skills)

    switch_to_game()

    pre_screen_shot_path, _ = gm.capture_screen()
    cur_screen_shot_path = pre_screen_shot_path
    success = False
    pre_skill = "None"
    pre_reasoning = "None"

    while not success:
        # for decision making
        input = planner.decision_making_.input_map

        number_of_execute_skills = input["number_of_execute_skills"]

        if pre_skill != "None":
            #input["previous_action"] = "Your previous executed skill is " + pre_skill + "."
            input["previous_action"] = memory.get_prev_action(k=1)[-1]
            input["previous_reasoning"] = memory.get_prev_reasoning(k=1)[-1]

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

        exec_info = gm.execute_actions(skill_steps)

        pre_skill = exec_info["last_skill"] # exec_info also has the list of successfully executed skills. skill_steps is the full list, which may differ if there were execution errors.

        pre_reasoning = ''
        if 'res_dict' in data.keys() and 'reasoning' in data['res_dict'].keys():
            pre_reasoning = data['res_dict']['reasoning']

        memory.add_history(
            {
                "skill": pre_skill,
                "reasoning": pre_reasoning,
            }
        )

        # For such cases with no expected response, we should define a retry limit

        logger.write(f'Decision reasoning: {pre_reasoning}')

        pre_screen_shot_path = cur_screen_shot_path
        cur_screen_shot_path, _ = gm.capture_screen()

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
        input["previous_action"] = memory.get_prev_action(k=1)
        input["previous_reasoning"] = memory.get_prev_reasoning(k=1)

        data = planner.success_detection(input = input)

        success = data['outcome']
        success_reasoning = data['res_dict']['decision']['reasoning']
        logger.write(f'Success: {success}')
        logger.write(f'Success reason: {success_reasoning}')

if __name__ == '__main__':

    config.set_fixed_seed()

    # main_test_decision_making()

    # main_test_success_detection()

    main_pipeline()