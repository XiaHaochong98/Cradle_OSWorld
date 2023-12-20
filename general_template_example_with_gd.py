import os
import time

from groundingdino.util.inference import load_model, load_image, predict
import cv2
import torch

from uac.config import Config
from uac.gameio.game_manager import GameManager
from uac.log import Logger
from uac.agent import Agent
from uac.planner.planner import Planner
from uac.memory.interface import MemoryInterface
from uac.memory.faiss import FAISS
from uac.provider.openai import OpenAIProvider
from uac.gameio.lifecycle.ui_control import switch_to_game, annotate_with_coordinates
from uac.gameio.atomic_skills.trade_utils import __all__ as trade_skills
from uac.gameio.atomic_skills.buy import __all__ as buy_skills
from uac.gameio.atomic_skills.map import __all__ as map_skills
from uac.gameio.atomic_skills.move import __all__ as move_skills
from uac.utils.file_utils import read_resource_file

config = Config()
logger = Logger()


# @TODO this should be changed to use the GdProvider
model = load_model("./cache/GroundingDINO_SwinB_cfg.py", "./cache/groundingdino_swinb_cogcoor.pth")

TEXT_PROMPT = "person."
BOX_TRESHOLD = 0.4
TEXT_TRESHOLD = 0.25

def main_test_decision_making(planner_params, task_description, skill_library):
    llm_provider_config_path = './conf/openai_config.json'

    llm_provider = OpenAIProvider()
    llm_provider.init_provider(llm_provider_config_path)
    planner = Planner(llm_provider=llm_provider,
                      planner_params=planner_params)
    input = planner.decision_making_.input_map

    gm = GameManager(config.env_name)

    skill_library = gm.get_filtered_skills(skill_library)

    image_introduction = [
        # {
        #     "introduction": "Here are some examples of trading in the game.",
        #     "path": "",
        #     "assistant": ""
        # },
        # {
        #     "introduction": "This example shows that the CARROT is currently selected in the image.",
        #     "path": r"\UAC\runs\1701163597.4037797\screen_1701163732.2476993.jpg",
        #     "assistant": "Yes. That is correct!"
        # },
        # {
        #     "introduction": "This example shows that the Canned SALMON is currently selected in the image.",
        #     "path": r"\UAC\runs\1701163597.4037797\screen_1701163680.5057523.jpg",
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
    input["task_description"] = task_description
    

    input['skill_library'] = skill_library
    input["previous_action"] = "view_next_page()"
    # input["previous_reasoning"] = "The current page displayed is the 'Canned Food' section of the Wheeler, Rawson & Co. catalogue, which includes a variety of canned goods. Items on the page, from the top left and moving to the right, are: Big Valley Canned Apricots, Schmitz Baked Beans, Flock of Sparrows Canned Kidney Beans, Big Valley Canned Peaches, Edna McSweeney Brand Canned Corned Beef, Blackwing Foods Canned Sweetcorn, Dewberry Brand Canned Peas, and Big Valley Canned Pineapples. The currently selected item is 'Canned Apricots' as indicated by the box around the item's description at the bottom of the screen. The target item, which is an 'Apple,' is not depicted on the current screen as these are all canned goods and do not include fresh produce. Therefore, the next logical step would be to navigate to the next page, which likely contains the Fresh Food section, with the hope of finding an apple there."
    # input["previous_reasoning"] = "1. The current screen displays four canned food items laid out in a two by two grid. From top left and moving right, the first item is 'Big Valley Canned Apricots,' next to it is 'Schmitz Baked Beans.' Below the apricots are 'Edna Mcsweeney Brand Canned Corned Beef,' and to the right of that is 'Blackwing Foods Canned Sweetcorn.' 2. The target item, an 'APPLE,' is not visible on the current screen, as these are canned goods and not fresh produce. 3. The item currently selected is 'Big Valley Canned Apricots,' as indicated by the detailed information shown at the bottom of the screen. Since the target item is an apple and should be under the 'Fresh Food' category, we should proceed to view the next page in the catalogue to find it."

    input["previous_reasoning"] = "1. The current screen displays various canned food products available for purchase in the Wheeler, Rawson & Co. catalog, with a focus on Big Valley canned apricots, Schmitz baked beans, Flock of Sparrows canned kidney beans, Big Valley canned peaches, Blackwing Foods canned sweetcorn, and Dewberry Brand canned peas. Each item is displayed with an image, a name, and a price listed below it. The player has $206.92 available, as indicated in the top right corner of the screen. 2. The target item, which is an 'APPLE', does not appear on the current screen. The items listed are all canned goods and do not include fresh fruit. 3. No specific item is currently selected for purchase, as the focus seems to be on the general canned goods page without any individual selection highlight present. The player appears to be in browse mode of the catalog, likely needing to navigate further to find the 'Fresh Food' section where an apple would be listed."

    data = planner.decision_making(input = input)

    skill_steps = data['res_dict']['actions']
    if skill_steps is None:
        skill_steps = []

    logger.write(f'Skill Steps: {skill_steps}')
    pre_reasoning = ''
    if 'res_dict' in data.keys() and 'reasoning' in data['res_dict'].keys():
        pre_reasoning = data['res_dict']['reasoning']

    # For such cases with no expected response, we should define a retry limit
    logger.write(f'Decision reasoning: {pre_reasoning}')

def main_test_success_detection(planner_params, task_description):
    llm_provider_config_path = './conf/openai_config.json'

    llm_provider = OpenAIProvider()
    llm_provider.init_provider(llm_provider_config_path)
    planner = Planner(llm_provider=llm_provider,
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
    input["task_description"] = task_description

    pre_action = 'buy_product()'
    pre_reasoning = "1. The items on the screen from top left moving right are: Big Valley Canned Strawberries, Schmitz Canned Salmon, a warning advertisement, Local Produce Apple, Local Produce Corn, Local Produce Carrot. 2. Yes, the target item 'Apple' is on the current screen, located under the 'Local Produce' section in the top right quadrant. 3. The currently selected item is the Apple, as indicated by the highlighted description at the bottom of the screen which says 'Apple'. Since the target item 'Apple' is selected, the next action is to purchase it."

    input["previous_action"] = pre_action
    input["previous_reasoning"] = pre_reasoning

    data = planner.success_detection(input = input)

    res_dict = data['res_dict']
    reasoning = res_dict['reasoning']
    criteria = res_dict['criteria']
    success = res_dict['success']

    logger.write(f'Success: {success}')
    logger.write(f'Criteria: {criteria}')
    logger.write(f'Reasoning: {reasoning}')


def main_pipeline(planner_params, task_description, skill_library):
    llm_provider_config_path = './conf/openai_config.json'

    llm_provider = OpenAIProvider()
    llm_provider.init_provider(llm_provider_config_path)

    planner = Planner(llm_provider=llm_provider,
                      planner_params=planner_params)
    
    recent_history = {"image": [], "action": [], "decision_making_reasoning": [], "success_detection_reasoning": [], "reflection_reasoning": []}
    vectorstore = FAISS(embedding_provider = llm_provider, memory_path = './res/memory')
    memory = MemoryInterface(
        memory_path='./res/memory',
        vectorstores = {"basic_memory":{"description":vectorstore},'decision_making':{},'success_detection':{}}, 
        embedding_provider=llm_provider,
        recent_history=recent_history,
        max_recent_steps=5
    )

    gm = GameManager(config.env_name)

    #skill_library = gm.get_filtered_skills(trade_skills + buy_skills)

    skill_library = gm.get_filtered_skills(skill_library)

    switch_to_game()

    cur_screen_shot_path, _ = gm.capture_screen()
    memory.add_recent_history("image", cur_screen_shot_path)
    
    if task_description in ["Your task is to approach the shopkeeper.", "Your task is to enter the store."]:
        image_source, image = load_image(cur_screen_shot_path)
        boxes, logits, phrases = predict(
            model=model,
            image=image,
            caption=TEXT_PROMPT,
            box_threshold=BOX_TRESHOLD,
            text_threshold=TEXT_TRESHOLD,
            device = 'cpu'
        )
        # logger.write(f'boxes: {boxes}')
        # logger.write(f'logits: {logits}')
        
        if "person" in TEXT_PROMPT:
            if len(boxes) > 1:
                index = 0
                dis = 1.5

                for i in range(len(boxes)):

                    down_mid = (boxes[i, 0], boxes[i, 1] + boxes[i, 3] / 2)
                    distance = torch.sum(torch.abs(torch.tensor(down_mid) - torch.tensor((0.5, 1.0))))

                    if distance < dis:
                        dis = distance
                        index = i
                
                boxes_ = torch.cat([boxes[:index], boxes[index + 1:]])
                logits_ = torch.cat([logits[:index], logits[index + 1:]])

                phrases.pop(index)
                
                annotated_frame = annotate_with_coordinates(image_source=image_source, boxes=boxes_, logits=logits_, phrases=phrases)
                cv2.imwrite(cur_screen_shot_path, annotated_frame)
            elif len(boxes)==1:

                boxes_ = torch.tensor(boxes[1:])
                logits_ = torch.tensor(logits[1:])
                phrases.pop(0)
                
                annotated_frame = annotate_with_coordinates(image_source=image_source, boxes=boxes_, logits=logits_, phrases=phrases)
                cv2.imwrite(cur_screen_shot_path, annotated_frame)
            else:
                annotated_frame = annotate_with_coordinates(image_source=image_source, boxes=boxes[:,:], logits=logits[:], phrases=phrases)
                cv2.imwrite(cur_screen_shot_path, annotated_frame)
            
        else:
            annotated_frame = annotate_with_coordinates(image_source=image_source, boxes=boxes[:,:], logits=logits[:], phrases=phrases)
            cv2.imwrite(cur_screen_shot_path, annotated_frame)
    

    success = False
    pre_action = ""
    pre_reasoning = ""
    # image_template_copy = copy.deepcopy(planner.decision_making_.input_map)
    image_template_copy = [
        {
            "introduction": "This is an example: the bounding box is on the left side (not slightly left) on the image",
            "path": "res/samples/few_shot_leftside.jpg",
            "assistant": "Yes, it is on the left side"
        },
        {
            "introduction": "This is an example: the bounding box is on the slightly left side (not left) on the image",
            "path": "res/samples/few_shot_slightly_leftside.jpg",
            "assistant": "Yes, it is on the slightly left side"
        },
        {
            "introduction": "This is an example: the bounding box is on the right side (not slightly right) on the image",
            "path": "res/samples/few_shot_rightside.jpg",
            "assistant": "Yes, it is on the right side"
        },
        {
            "introduction": "This is an example: the bounding box is on the slightly right side (not right) on the image",
            "path": "res/samples/few_shot_slightly_rightside.jpg",
            "assistant": "Yes, it is on the slightly right side"
        },
        {
            "introduction": "This is an example: the bounding box is on the central on the image",
            "path": "res/samples/few_shot_central.jpg",
            "assistant": "Yes, it is on the central side"
        },
        {
            "introduction": "This screenshot is four step before the previous step of the game",
            "path": "",
            "assistant": ""
        },
        {
            "introduction": "This screenshot is three step before the previous step of the game",
            "path": "",
            "assistant": ""
        },
        {
            "introduction": "This screenshot is two step before the previous step of the game",
            "path": "",
            "assistant": ""
        },
        {
            "introduction": "This screenshot is one step before the previous step of the game",
            "path": "",
            "assistant": ""
        },
        {
            "introduction": "This screenshot is the previous step of the game",
            "path": "res/prompts/testing/decision_making/buy/10.jpg",
            "assistant": ""
        },
        {
            "introduction": "This screenshot is the current step of the game",
            "path": "res/prompts/testing/decision_making/buy/11.jpg",
            "assistant": ""
        }
    ]
    
    while not success:
        # for decision making
        input = planner.decision_making_.input_map

        number_of_execute_skills = input["number_of_execute_skills"]

        if pre_action:
            input["previous_action"] = memory.get_recent_history("action", k=1)[-1]
            input["previous_reasoning"] = memory.get_recent_history("decision_making_reasoning", k=1)[-1]

        input['skill_library'] = skill_library
        
        image_memory = memory.get_recent_history("image", k=5)
        image_introduction = []
        for i in range(len(image_memory)):
            image_introduction.insert(0,            
                {
                    "introduction": image_template_copy[-1-i]["introduction"],
                    "path":image_memory[-1-i],
                    "assistant": ""
                })
        # loading few shots
        if task_description in ["Your task is to approach the shopkeeper.", "Your task is to enter the store."]:
            for i in range(5):
                image_introduction.insert(0,            
                    {
                        "introduction": image_template_copy[i]["introduction"],
                        "path":image_template_copy[i]["path"],
                        "assistant": image_template_copy[i]["assistant"]
                    })

        # logger.write(f'image_introduction: {image_introduction}')
        
        input["image_introduction"] = image_introduction
        input["task_description"] = task_description

        data = planner.decision_making(input = input)

        skill_steps = data['res_dict']['actions']
        if skill_steps is None:
            skill_steps = []

        logger.write(f'R: {skill_steps}')

        skill_steps = skill_steps[:number_of_execute_skills]
        logger.write(f'Skill Steps: {skill_steps}')

        exec_info = gm.execute_actions(skill_steps)

        pre_action = exec_info["last_skill"] # exec_info also has the list of successfully executed skills. skill_steps is the full list, which may differ if there were execution errors.

        pre_reasoning = ''
        if 'res_dict' in data.keys() and 'reasoning' in data['res_dict'].keys():
            pre_reasoning = data['res_dict']['reasoning']

        memory.add_recent_history("action", pre_action)
        memory.add_recent_history("decision_making_reasoning", pre_reasoning)

        # For such cases with no expected response, we should define a retry limit

        logger.write(f'Decision reasoning: {pre_reasoning}')

        cur_screen_shot_path, _ = gm.capture_screen()
        memory.add_recent_history("image", cur_screen_shot_path)
        
        if task_description in ["Your task is to approach the shopkeeper.", "Your task is to enter the store."]:
            image_source, image = load_image(cur_screen_shot_path)
            boxes, logits, phrases = predict(
                model=model,
                image=image,
                caption=TEXT_PROMPT,
                box_threshold=BOX_TRESHOLD,
                text_threshold=TEXT_TRESHOLD,
                device = 'cpu'
            )
            
            if "person" in TEXT_PROMPT:
                if len(boxes) > 1:
                    index = 0
                    dis = 1.5

                    for i in range(len(boxes)):
                        down_mid = (boxes[i, 0], boxes[i, 1] + boxes[i, 3] / 2)
                        distance = torch.sum(torch.abs(torch.tensor(down_mid) - torch.tensor((0.5, 1.0))))

                        if distance < dis:
                            dis = distance
                            index = i
                    
                    boxes_ = torch.cat([boxes[:index], boxes[index + 1:]])
                    logits_ = torch.cat([logits[:index], logits[index + 1:]])

                    phrases.pop(index)
                    
                    annotated_frame = annotate_with_coordinates(image_source=image_source, boxes=boxes_[:,:], logits=logits_[:], phrases=phrases)
                    cv2.imwrite(cur_screen_shot_path, annotated_frame)
                elif len(boxes)==1:

                    phrases.pop(0)
                    boxes_ = torch.tensor(boxes[1:])
                    logits_ = torch.tensor(logits[1:])

                    annotated_frame = annotate_with_coordinates(image_source=image_source, boxes=boxes_[:,:], logits=logits_[:], phrases=phrases)
                    cv2.imwrite(cur_screen_shot_path, annotated_frame)
                else:
                    annotated_frame = annotate_with_coordinates(image_source=image_source, boxes=boxes[:,:], logits=logits[:], phrases=phrases)
                    cv2.imwrite(cur_screen_shot_path, annotated_frame)
                
            else:
                annotated_frame = annotate_with_coordinates(image_source=image_source, boxes=boxes[:,:], logits=logits[:], phrases=phrases)
                cv2.imwrite(cur_screen_shot_path, annotated_frame)

        # for success detection
        input = planner.success_detection_.input_map
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
        input["task_description"] = task_description
        input["previous_action"] = memory.get_recent_history("action", k=1)[-1]
        input["previous_reasoning"] = memory.get_recent_history("decision_making_reasoning", k=1)[-1]

        data = planner.success_detection(input = input)

        success = data['res_dict']['success']
        success_reasoning = data['res_dict']['reasoning']
        success_criteria = data['res_dict']['criteria']
        memory.add_recent_history("success_detection_reasoning", success_reasoning)
        logger.write(f'Success: {success}')
        logger.write(f'Success criteria: {success_criteria}')
        logger.write(f'Success reason: {success_reasoning}')

if __name__ == '__main__':

    # only change the input for different 
    # the tempaltes are now fixed

    planner_params = {
        "__check_list__": [
            "decision_making",
            "gather_information",
            "success_detection",
            "information_summary"
        ],
        "prompt_paths": {
            "inputs": {
                "decision_making": "./res/prompts/inputs/decision_making.json",
                "gather_information": "./res/prompts/inputs/gather_information.json",
                "success_detection": "./res/prompts/inputs/success_detection.json",
                "information_summary": "./res/prompts/inputs/information_summary.json"
            },
            "templates": {
                "decision_making": "./res/prompts/templates/decision_making.prompt",
                "gather_information": "./res/prompts/templates/gather_information.prompt",
                "success_detection": "./res/prompts/templates/success_detection.prompt",
                "information_summary": "./res/prompts/templates/information_summary.prompt"
            },
        }
    }

    # # map_create_waypoint
    # skill_library = map_skills
    # task_description = "Mark the \"Saloon\" on a Map as the Waypoint via the Index."

    # buy_item
    # skill_library = trade_skills + buy_skills
    # task_description = "Your task is to buy one 'APPLE'."

    # enter the store
    # skill_library = move_skills
    # task_description =  "Your task is to enter the store."

    # approach the shopkeeper
    skill_library = move_skills
    task_description =  "Your task is to approach the shopkeeper."

    config.set_fixed_seed()

    #main_test_decision_making(planner_params, task_description, skill_library)

    #main_test_success_detection(planner_params, task_description)

    main_pipeline(planner_params, task_description, skill_library)