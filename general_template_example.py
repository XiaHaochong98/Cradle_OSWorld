import os
import cv2
import time

from uac.config import Config
from uac.gameio.game_manager import GameManager
from uac.log import Logger
from uac.agent import Agent
from uac.planner.planner import Planner
from uac.memory import LocalMemory
from uac.provider.openai import OpenAIProvider
from uac.provider import GdProvider
from uac.gameio.io_env import IOEnvironment
from uac.gameio.lifecycle.ui_control import switch_to_game, IconReplacer
from uac.gameio.video.VideoRecorder import VideoRecorder
from uac.gameio.video.VideoFrameExtractor import VideoFrameExtractor
from uac.gameio.atomic_skills.trade_utils import __all__ as trade_skills
from uac.gameio.atomic_skills.buy import __all__ as buy_skills
from uac.gameio.atomic_skills.map import __all__ as map_skills
from uac.gameio.atomic_skills.move import __all__ as move_skills
from uac.gameio.atomic_skills.combat import __all__ as combat_skills
from uac.gameio.composite_skills.auto_shoot import __all__ as auto_shoot_skills
from uac.gameio.composite_skills.follow import __all__ as follow_skills
from uac import constants
from uac.gameio.skill_registry import SkillRegistry
import copy
from groundingdino.util.inference import load_image

config = Config()
logger = Logger()
io_env = IOEnvironment()


def main_test_decision_making(planner_params, task_description, skill_library):
    llm_provider_config_path = './conf/openai_config.json'

    llm_provider = OpenAIProvider()
    llm_provider.init_provider(llm_provider_config_path)
    planner = Planner(llm_provider=llm_provider,
                      planner_params=planner_params)
    input = planner.decision_making_.input_map

    gm = GameManager(env_name = config.env_name,
                     embedding_provider = llm_provider)

    if config.skill_retrieval:
        skill_library = gm.retrieve_skills(query_task = task_description, skill_num = config.skill_num)
    skill_library = gm.get_skill_information(skill_library)

    image_introduction = [
        {
            "introduction": input["image_introduction"][-2]["introduction"],
            "path": "./res/prompts/testing/decision_making/buy/4.jpg",
            "assistant": input["image_introduction"][-2]["assistant"]
        },
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": "./res/prompts/testing/decision_making/buy/5.jpg",
            "resolution": "high",
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
    pre_decision_making_reasoning = ''
    if 'res_dict' in data.keys() and 'reasoning' in data['res_dict'].keys():
        pre_decision_making_reasoning = data['res_dict']['reasoning']

    # For such cases with no expected response, we should define a retry limit
    logger.write(f'Decision reasoning: {pre_decision_making_reasoning}')


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
            "path": "./res/prompts/testing/decision_making/buy/7.jpg",
            "assistant": input["image_introduction"][-2]["assistant"]
        },
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": "./res/prompts/testing/decision_making/buy/8.jpg",
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]
    input["image_introduction"] = image_introduction
    input["task_description"] = task_description

    pre_action = 'buy_product()'
    pre_decision_making_reasoning = "1. The items on the screen from top left moving right are: Big Valley Canned Strawberries, Schmitz Canned Salmon, a warning advertisement, Local Produce Apple, Local Produce Corn, Local Produce Carrot. 2. Yes, the target item 'Apple' is on the current screen, located under the 'Local Produce' section in the top right quadrant. 3. The currently selected item is the Apple, as indicated by the highlighted description at the bottom of the screen which says 'Apple'. Since the target item 'Apple' is selected, the next action is to purchase it."

    input["previous_action"] = pre_action
    input["previous_reasoning"] = pre_decision_making_reasoning

    data = planner.success_detection(input = input)

    res_dict = data['res_dict']
    reasoning = res_dict['reasoning']
    criteria = res_dict['criteria']
    success = res_dict['success']

    logger.write(f'Success: {success}')
    logger.write(f'Criteria: {criteria}')
    logger.write(f'Reasoning: {reasoning}')


def main_test_information_summary(planner_params, task_description, skill_library):
    llm_provider_config_path = './conf/openai_config.json'

    llm_provider = OpenAIProvider()
    llm_provider.init_provider(llm_provider_config_path)

    planner = Planner(llm_provider=llm_provider,
                      planner_params=planner_params,
                      use_information_summary = True)

    memory = LocalMemory(memory_path=config.work_dir,
                         max_recent_steps=config.max_recent_steps)

    gm = GameManager(env_name = config.env_name,
                     embedding_provider = llm_provider)

    if config.skill_retrieval:
        skill_library = gm.retrieve_skills(query_task = task_description, skill_num = config.skill_num)
    skill_library = gm.get_skill_information(skill_library)

    switch_to_game()

    cur_screen_shot_path, _ = gm.capture_screen()
    memory.add_recent_history("image", cur_screen_shot_path)

    success = False
    pre_action = ""
    pre_decision_making_reasoning = ""
    event_count = min(config.event_count, config.max_recent_steps)

    while not success:
        # for decision making
        input = planner.decision_making_.input_map

        number_of_execute_skills = input["number_of_execute_skills"]

        if pre_action:
            input["previous_action"] = memory.get_recent_history("action", k=1)[-1]
            input["previous_reasoning"] = memory.get_recent_history("decision_making_reasoning", k=1)[-1]

        input['skill_library'] = skill_library

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

        data = planner.decision_making(input = input)

        skill_steps = data['res_dict']['actions']
        if skill_steps is None:
            skill_steps = []

        logger.write(f'R: {skill_steps}')

        skill_steps = skill_steps[:number_of_execute_skills]
        logger.write(f'Skill Steps: {skill_steps}')

        exec_info = gm.execute_actions(skill_steps)

        pre_action = exec_info["last_skill"] # exec_info also has the list of successfully executed skills. skill_steps is the full list, which may differ if there were execution errors.

        pre_decision_making_reasoning = ''
        if 'res_dict' in data.keys() and 'reasoning' in data['res_dict'].keys():
            pre_decision_making_reasoning = data['res_dict']['reasoning']

        memory.add_recent_history("action", pre_action)
        memory.add_recent_history("decision_making_reasoning", pre_decision_making_reasoning)

        # For such cases with no expected response, we should define a retry limit

        logger.write(f'Decision reasoning: {pre_decision_making_reasoning}')

        cur_screen_shot_path, _ = gm.capture_screen()
        memory.add_recent_history("image", cur_screen_shot_path)

        ## summary begins
        if len(memory.get_recent_history("decision_making_reasoning", memory.max_recent_steps)) == memory.max_recent_steps:
            input = planner.information_summary_.input_map
            logger.write(f'> Information summary call...')
            images = memory.get_recent_history('image', event_count)
            reasonings = memory.get_recent_history('decision_making_reasoning', event_count)
            image_introduction = [{"path": images[event_i],"assistant": "","introduction": 'This is the {} screenshot of recent events. The description of this image: {}'.format(['first','second','third','fourth','fifth'][event_i], reasonings[event_i])} for event_i in range(event_count)]

            input["image_introduction"] = image_introduction
            input["previous_summarization"] = memory.get_summarization()
            input["task_description"] = task_description
            input["event_count"] = str(event_count)

            data = planner.information_summary(input = input)
            info_summary = data['res_dict']['info_summary']
            entities_and_behaviors = data['res_dict']['entities_and_behaviors']
            logger.write(f'R: Summary: {info_summary}')
            logger.write(f'R: entities_and_behaviors: {entities_and_behaviors}')
            memory.add_summarization(info_summary)
        summarization = memory.get_summarization()
        ## summary ends

        #store memory
        gm.store_skills()
        memory.save()


def main_test_self_reflection(planner_params, task_description, skill_library, video_path):
    llm_provider_config_path = './conf/openai_config.json'

    llm_provider = OpenAIProvider()
    llm_provider.init_provider(llm_provider_config_path)
    planner = Planner(llm_provider=llm_provider,
                      planner_params=planner_params,
                      use_self_reflection=True)

    input = planner.self_reflection_.input_map

    image_introduction = []
    video = cv2.VideoCapture(video_path)
    step = 0
    video_frames = []
    action_frames = []
    while True:
        ret, frame = video.read()
        if not ret:
            break
        # path = 'test/' + str(step) + ".jpg"
        # cv2.imwrite(path, frame)
        #image_path.append(path)
        video_frames.append((step, frame))
        step += 1
    video.release()

    if len(video_frames) <= config.max_images_in_self_reflection * config.duplicate_frames + 1:
        action_frames = [frame[1] for frame in video_frames[1::config.duplicate_frames]]
    else:
        for i in range(config.max_images_in_self_reflection):
            step = len(video_frames) // config.max_images_in_self_reflection * i + 1
            action_frames.append(video_frames[step][1])

    image_introduction = [
        {
            "introduction": "Here are the sequential frames of the character executing the last action. Is this action executed successfully? Does this action takes any effect? Does this action contributes to the task? If not, what would be a better action based on the last screenshot?",
            "path": action_frames,
            "assistant": "",
            "resolution": "low"
    }]

    input["image_introduction"] = image_introduction
    input["task_description"] = task_description

    pre_action = 'move_forward(duration=1)'
    pre_decision_making_reasoning = ""

    input["previous_action"] = pre_action
    input["previous_reasoning"] = pre_decision_making_reasoning

    data = planner.self_reflection(input = input)

    res_dict = data['res_dict']
    reasoning = res_dict['reasoning']

    logger.write(f'Reasoning: {reasoning}')

def skill_library_test():

    provider_config_path = './conf/openai_config.json'
    provider = OpenAIProvider()
    provider.init_provider(provider_config_path)

    config.skill_from_local = True

    gm = GameManager(env_name = config.env_name, embedding_provider=provider)


    task_description = "Mark the \"Saloon\" on a Map as the Waypoint via the Index."

    extracted_skills = ["def pick_up_item_t():\n    \"\"\"\n    Presses the E key to pick up nearby items.\n    \"\"\"\n    pydirectinput.press('e')\n",
                        "def go_ahead_t(duration):\n    \"\"\"\n    Moves the in-game character forward for the specified duration.\n\nParameters:\n- duration: The duration in seconds for which the character should move forward.\n    \"\"\"\n    pydirectinput.keyDown('w')\n    time.sleep(duration)\n    pydirectinput.keyUp('w')\n"]

    for extracted_skill in extracted_skills:
        gm.add_new_skill(skill_code=extracted_skill)

    exec_info = gm.execute_actions(['go_ahead_t(duration = 1)'])
    logger.write(str(exec_info))

    exec_info = gm.execute_actions(['pick_up_item_t()'])
    logger.write(str(exec_info))

    returns_skills = gm.retrieve_skills(query_task = task_description, skill_num = config.skill_num)
    logger.write(str(returns_skills))
    logger.write(str(gm.get_skill_information(returns_skills)))


    returns_skills = gm.retrieve_skills(query_task = task_description, skill_num = config.skill_num)
    logger.write(str(returns_skills))


    skill_library = move_skills + follow_skills
    gm.register_available_skills(skill_library)

    returns_skills = gm.retrieve_skills(query_task = task_description, skill_num = config.skill_num)
    logger.write(str(returns_skills))

    gm.store_skills()


def main_gather_information(image_path = ""):
    llm_provider_config_path = './conf/openai_config.json'

    llm_provider = OpenAIProvider()
    llm_provider.init_provider(llm_provider_config_path)

    gd_detector = GdProvider()

    frame_extractor = VideoFrameExtractor()

    planner = Planner(llm_provider=llm_provider,
                      planner_params=planner_params,
                      frame_extractor=frame_extractor,
                      object_detector=gd_detector,
                      use_self_reflection=False,
                      use_information_summary=False)


    input = planner.gather_information_.input_map
    text_input = planner.gather_information_.text_input_map

    get_text_image_introduction = [
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": image_path,
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]

    #configure the gather_information module
    gather_information_configurations = {
        "frame_extractor": False, # extract text from the video clip
        "icon_replacer": False,
        "llm_description": True, # get the description of the current screenshot
        "object_detector": False
    }

    input["gather_information_configurations"] = gather_information_configurations
    # modify the general input for gather_information here
    image_introduction=[get_text_image_introduction[-1]]
    input["task_description"] = task_description
    input["video_clip_path"] = ""
    input["image_introduction"] = image_introduction
    # Modify the input for get_text module in gather_information here
    text_input["image_introduction"] = get_text_image_introduction
    input["text_input"] = text_input

    data = planner.gather_information(input=input)

    image_description=data['res_dict'][constants.IMAGE_DESCRIPTION]
    target_object_name=data['res_dict'][constants.TARGET_OBJECT_NAME]
    object_name_reasoning=data['res_dict'][constants.GATHER_INFO_REASONING]
    screen_classification=data['res_dict'][constants.SCREEN_CLASSIFICATION]

    logger.write(f'Image Description: {image_description}')
    logger.write(f'Object Name: {target_object_name}')
    logger.write(f'Reasoning: {object_name_reasoning}')
    logger.write(f'Screen Classification: {screen_classification}')

def main_test_gather_information(image_path = "", video_path = ""):
    llm_provider_config_path = './conf/openai_config.json'

    llm_provider = OpenAIProvider()
    llm_provider.init_provider(llm_provider_config_path)

    gd_detector = GdProvider()

    frame_extractor = VideoFrameExtractor()
    icon_replacer = IconReplacer()

    planner = Planner(llm_provider=llm_provider,
                      planner_params=planner_params,
                      frame_extractor=frame_extractor,
                      icon_replacer=icon_replacer,
                      object_detector=gd_detector,
                      use_self_reflection=False,
                      use_information_summary=False)


    input = planner.gather_information_.input_map
    text_input = planner.gather_information_.text_input_map

    get_text_image_introduction = [
        {
            "introduction": input["image_introduction"][-1]["introduction"],
            "path": image_path,
            "assistant": input["image_introduction"][-1]["assistant"]
        }
    ]

    #configure the gather_information module
    gather_information_configurations = {
        "frame_extractor": True, # extract text from the video clip
        "icon_replacer": True,
        "llm_description": False, # get the description of the current screenshot
        "object_detector": False
    }

    input["gather_information_configurations"] = gather_information_configurations
    # modify the general input for gather_information here
    image_introduction=[get_text_image_introduction[-1]]
    input["task_description"] = task_description
    input["video_clip_path"] = video_path
    input["image_introduction"] = image_introduction
    # Modify the input for get_text module in gather_information here
    text_input["image_introduction"] = get_text_image_introduction
    input["text_input"] = text_input

    input["test_text_image"] = image_path

    # >> Calling INFORMATION GATHERING
    logger.write(f'>> Calling INFORMATION GATHERING')
    data = planner.gather_information(input=input)

    # you can extract any information from the gathered_information_JSON
    gathered_information_JSON=data['res_dict']['gathered_information_JSON']

    if gathered_information_JSON is not None:
        gathered_information=gathered_information_JSON.data_structure
    else:
        logger.warn("NO data_structure in gathered_information_JSON")
        gathered_information = dict()

    # sort the gathered_information by the time stamp
    gathered_information = dict(sorted(gathered_information.items(), key=lambda item: item[0]))
    all_dialogue = gathered_information_JSON.search_type_across_all_indices(constants.DIALOGUE)
    all_task_guidance = gathered_information_JSON.search_type_across_all_indices(constants.TASK_GUIDANCE)
    all_generated_actions = gathered_information_JSON.search_type_across_all_indices(constants.ACTION_GUIDANCE)
    classification_reasons = gathered_information_JSON.search_type_across_all_indices(constants.GATHER_TEXT_REASONING)

    logger.write(f'Dialogue: {all_dialogue}')
    #logger.write(f'Gathered Information: {gathered_information}')
    logger.write(f'Classification Reasons: {classification_reasons}')
    #logger.write(f'All Task Guidance: {all_task_guidance}')
    logger.write(f'Generated Actions: {all_generated_actions}')


def main_pipeline(planner_params, task_description, skill_library, use_success_detection = False, use_self_reflection = False, use_information_summary = False):

    llm_provider_config_path = './conf/openai_config.json'

    llm_provider = OpenAIProvider()
    llm_provider.init_provider(llm_provider_config_path)

    gd_detector = GdProvider()

    frame_extractor = VideoFrameExtractor()
    icon_replacer = IconReplacer()

    planner = Planner(llm_provider=llm_provider,
                      planner_params=planner_params,
                      frame_extractor=frame_extractor,
                      icon_replacer=icon_replacer,
                      object_detector=gd_detector,
                      use_self_reflection=use_self_reflection,
                      use_information_summary=use_information_summary)

    memory = LocalMemory(memory_path=config.work_dir,
                         max_recent_steps=config.max_recent_steps)
    memory.load(config.memory_load_path)

    gm = GameManager(env_name = config.env_name,
                     embedding_provider = llm_provider)

    img_prompt_decision_making = planner.decision_making_.input_map["image_introduction"]

    if config.skill_retrieval:
        gm.register_available_skills(skill_library)
        skill_library = gm.retrieve_skills(query_task = task_description, skill_num = config.skill_num)
    skill_library = gm.get_skill_information(skill_library)

    switch_to_game()

    videocapture=VideoRecorder(os.path.join(config.work_dir, 'video.mp4'))
    videocapture.start_capture()
    start_frame_id = videocapture.get_current_frame_id()

    cur_screen_shot_path, _ = gm.capture_screen()
    memory.add_recent_history("image", cur_screen_shot_path)

    success = False
    pre_action = ""
    pre_screen_classification = ""
    pre_decision_making_reasoning = ""
    pre_self_reflection_reasoning = ""

    time.sleep(2)
    end_frame_id = videocapture.get_current_frame_id()
    gm.pause_game()

    while not success:

        try:
            #for gather information
            logger.write(f'Gather Information Start Frame ID: {start_frame_id}, End Frame ID: {end_frame_id}')
            input = planner.gather_information_.input_map
            text_input = planner.gather_information_.text_input_map
            video_clip_path = videocapture.get_video(start_frame_id,end_frame_id)
            videocapture.clear_frame_buffer()
            task_description = memory.get_task_guidance(use_last=False)

            get_text_image_introduction = [
                {
                    "introduction": input["image_introduction"][-1]["introduction"],
                    "path": memory.get_recent_history("image", k=1)[0],
                    "assistant": input["image_introduction"][-1]["assistant"]
                }
            ]

            #configure the gather_information module
            gather_information_configurations = {
                "frame_extractor": True, # extract text from the video clip
                "icon_replacer": True,
                "llm_description": True, # get the description of the current screenshot
                "object_detector": True
            }
            input["gather_information_configurations"] = gather_information_configurations

            # modify the general input for gather_information here
            image_introduction=[get_text_image_introduction[-1]]
            input["task_description"] = task_description
            input["video_clip_path"] = video_clip_path
            input["image_introduction"] = image_introduction

            # Modify the input for get_text module in gather_information here
            text_input["image_introduction"] = get_text_image_introduction
            input["text_input"] = text_input

            # >> Calling INFORMATION GATHERING
            logger.write(f'>> Calling INFORMATION GATHERING')
            data = planner.gather_information(input=input)

            # you can extract any information from the gathered_information_JSON
            gathered_information_JSON=data['res_dict']['gathered_information_JSON']

            if gathered_information_JSON is not None:
                gathered_information=gathered_information_JSON.data_structure
            else:
                logger.warn("NO data_structure in gathered_information_JSON")
                gathered_information = dict()

            # sort the gathered_information by the time stamp
            gathered_information = dict(sorted(gathered_information.items(), key=lambda item: item[0]))
            all_dialogue = gathered_information_JSON.search_type_across_all_indices(constants.DIALOGUE)
            all_task_guidance = gathered_information_JSON.search_type_across_all_indices(constants.TASK_GUIDANCE)
            all_generated_actions = gathered_information_JSON.search_type_across_all_indices(constants.ACTION_GUIDANCE)
            classification_reasons = gathered_information_JSON.search_type_across_all_indices(constants.GATHER_TEXT_REASONING)

            response_keys = data['res_dict'].keys()

            if constants.LAST_TASK_GUIDANCE in response_keys:
                last_task_guidance = data['res_dict'][constants.LAST_TASK_GUIDANCE]
                if constants.LAST_TASK_HORIZON in response_keys:
                    long_horizon = bool(int(data['res_dict'][constants.LAST_TASK_HORIZON][0])) # Only first character is relevant
                else:
                    long_horizon = False
            else:
                logger.warn(f"No {constants.LAST_TASK_GUIDANCE} in response.")
                last_task_guidance = ""
                long_horizon = False

            if constants.IMAGE_DESCRIPTION in response_keys:
                image_description=data['res_dict'][constants.IMAGE_DESCRIPTION]
                if constants.SCREEN_CLASSIFICATION in response_keys:
                    screen_classification=data['res_dict'][constants.SCREEN_CLASSIFICATION]
                else:
                    screen_classification="None"
            else:
                logger.warn(f"No {constants.IMAGE_DESCRIPTION} in response.")
                image_description="No description"
                screen_classification="None"

            if constants.TARGET_OBJECT_NAME in response_keys:
                target_object_name=data['res_dict'][constants.TARGET_OBJECT_NAME]
                object_name_reasoning=data['res_dict'][constants.GATHER_INFO_REASONING]
            else:
                logger.write("> No target object")
                target_object_name = ""
                object_name_reasoning=""

            if "boxes" in response_keys:
                image_source, image = load_image(cur_screen_shot_path)
                boxes = data['res_dict']["boxes"]
                logits = data['res_dict']["logits"]
                phrases = data['res_dict']["phrases"]
                directory, filename = os.path.split(cur_screen_shot_path)
                bb_image_path = os.path.join(directory, "bb_"+filename)
                gd_detector.save_annotate_frame(image_source, boxes, logits, phrases, target_object_name.title(), bb_image_path)

                if boxes is not None and boxes.numel() != 0:
                    #add the screenshot with bounding boxes into the local memory
                    memory.add_recent_history(key=constants.AUGMENTED_IMAGES_MEM_BUCKET, info=bb_image_path)
                else:
                    memory.add_recent_history(key=constants.AUGMENTED_IMAGES_MEM_BUCKET, info=constants.NO_IMAGE)
            else:
                memory.add_recent_history(key=constants.AUGMENTED_IMAGES_MEM_BUCKET, info=constants.NO_IMAGE)

            logger.write(f'Image Description: {image_description}')
            logger.write(f'Object Name: {target_object_name}')
            logger.write(f'Reasoning: {object_name_reasoning}')
            logger.write(f'Screen Classification: {screen_classification}')

            logger.write(f'Dialogue: {all_dialogue}')
            logger.write(f'Gathered Information: {gathered_information}')
            logger.write(f'Classification Reasons: {classification_reasons}')
            logger.write(f'All Task Guidance: {all_task_guidance}')
            logger.write(f'Last Task Guidance: {last_task_guidance}')
            logger.write(f'Long Horizon: {long_horizon}')
            logger.write(f'Generated Actions: {all_generated_actions}')

            if use_self_reflection and start_frame_id > -1:
                input = planner.self_reflection_.input_map
                action_frames = []
                video_frames = videocapture.get_frames(start_frame_id,end_frame_id)

                if len(video_frames) <= config.max_images_in_self_reflection * config.duplicate_frames + 1:
                    action_frames = [frame[1] for frame in video_frames[1::config.duplicate_frames]]
                else:
                    for i in range(config.max_images_in_self_reflection):
                        step = len(video_frames) // config.max_images_in_self_reflection * i + 1
                        action_frames.append(video_frames[step][1])

                image_introduction = [
                    {
                        "introduction": "Here are the sequential frames of the character executing the last action.",
                        "path": action_frames,
                        "assistant": "",
                        "resolution": "low"
                }]

                input["image_introduction"] = image_introduction
                #input["task_description"] = task_description
                input["task_description"] = task_description
                input['skill_library'] = skill_library
                input["previous_reasoning"] = pre_decision_making_reasoning

                if pre_action:
                    pre_action_name, pre_action_params = gm.skill_registry.convert_expression_to_skill(pre_action)
                    # only input the pre_action name
                    input["previous_action"] = pre_action_name
                    action_code, action_code_info = gm.get_skill_library_in_code(pre_action_name)
                    input['action_code'] = action_code if action_code is not None else action_code_info
                else:
                    input["previous_action"] = ""
                    input['action_code'] = ""

                if exec_info["errors"]:
                    input['executing_action_error']  = exec_info["errors_info"]
                else:
                    input['executing_action_error']  = ""

                # >> Calling SELF REFLECTION
                logger.write(f'>> Calling SELF REFLECTION')
                reflection_data = planner.self_reflection(input = input)

                if 'reasoning' in reflection_data['res_dict'].keys():
                    self_reflection_reasoning = reflection_data['res_dict']['reasoning']
                else:
                    self_reflection_reasoning = ""
                pre_self_reflection_reasoning = self_reflection_reasoning
                memory.add_recent_history("self_reflection_reasoning", self_reflection_reasoning)
                logger.write(f'Self-reflection reason: {self_reflection_reasoning}')

            if last_task_guidance:
                task_description = last_task_guidance
                memory.add_task_guidance(last_task_guidance, long_horizon)

            logger.write(f'Current Task Guidance: {task_description}')

            if config.skill_retrieval:
                for extracted_skills in all_generated_actions:
                    extracted_skills=extracted_skills['values']
                    for extracted_skill in extracted_skills:
                        gm.add_new_skill(skill_code=extracted_skill['code'])

                skill_library = gm.retrieve_skills(query_task = task_description, skill_num = config.skill_num)
                logger.write(f'skill_library: {skill_library}')
                skill_library = gm.get_skill_information(skill_library)

            # for decision making
            input = copy.deepcopy(planner.decision_making_.input_map)

            number_of_execute_skills = input["number_of_execute_skills"]

            if pre_action:
                input["previous_action"] = memory.get_recent_history("action", k=1)[-1]
                input["previous_reasoning"] = memory.get_recent_history("decision_making_reasoning", k=1)[-1]

            if pre_self_reflection_reasoning:
                input["previous_self_reflection_reasoning"] = memory.get_recent_history("self_reflection_reasoning", k=1)[-1]

            input['skill_library'] = skill_library
            input['info_summary'] = memory.get_summarization()

            if not "boxes" in response_keys:
                input['few_shots'] = []
            else:
                if boxes is None or boxes.numel() == 0:
                    input['few_shots'] = []

            #@TODO Temporary solution with fake augmented entries if no bounding box exists. Ideally it should read images, then check for possible augmentation.
            image_memory = memory.get_recent_history("image", k=config.decision_making_image_num)
            augmented_image_memory = memory.get_recent_history(constants.AUGMENTED_IMAGES_MEM_BUCKET, k=config.decision_making_image_num)

            image_introduction = []
            for i in range(len(image_memory), 0, -1):
                if augmented_image_memory[-i] != constants.NO_IMAGE:
                    image_introduction.append(
                        {
                            "introduction": img_prompt_decision_making[-i]["introduction"],
                            "path":augmented_image_memory[-i],
                            "assistant": img_prompt_decision_making[-i]["assistant"]
                        })
                else:
                    image_introduction.append(
                        {
                            "introduction": img_prompt_decision_making[-i]["introduction"],
                            "path":image_memory[-i],
                            "assistant": img_prompt_decision_making[-i]["assistant"]
                        })

            input["image_introduction"] = image_introduction
            input["task_description"] = task_description

            # newly add dino detection for minimap
            if constants.MINIMAP_INFORMATION in response_keys:
                minimap_information = data["res_dict"][constants.MINIMAP_INFORMATION]
                logger.write(f"{constants.MINIMAP_INFORMATION}: {minimap_information}")

                minimap_info_str = ""
                for key, value in minimap_information.items():
                    if value:
                        for index, item in enumerate(value):
                            minimap_info_str = minimap_info_str + key + ' ' + str(index) + ': angle '  + str(int(item['theta'])) + ' degree' + '\n'
                minimap_info_str = minimap_info_str.rstrip('\n')

                logger.write(f'minimap_info_str: {minimap_info_str}')
                input[constants.MINIMAP_INFORMATION] = minimap_info_str

            data = planner.decision_making(input = input)

            skill_steps = data['res_dict']['actions']
            if skill_steps is None:
                skill_steps = []

            logger.write(f'R: {skill_steps}')

            # Filter nop actions in list
            skill_steps = [ i for i in skill_steps if i != '']
            if len(skill_steps) == 0:
                skill_steps = ['']

            skill_steps = skill_steps[:number_of_execute_skills]
            logger.write(f'Skill Steps: {skill_steps}')

            gm.unpause_game()
            # TODO: find a better name of the GENERAL_GAME_INTERFACE
            if pre_screen_classification.lower() == constants.GENERAL_GAME_INTERFACE and screen_classification.lower() != constants.GENERAL_GAME_INTERFACE and pre_action:
                exec_info = gm.execute_actions([pre_action])

            start_frame_id = videocapture.get_current_frame_id()

            exec_info = gm.execute_actions(skill_steps)

            cur_screen_shot_path, _ = gm.capture_screen()

            end_frame_id = videocapture.get_current_frame_id()
            gm.pause_game()

            pre_action = exec_info["last_skill"] # exec_info also has the list of successfully executed skills. skill_steps is the full list, which may differ if there were execution errors.

            pre_decision_making_reasoning = ''
            if 'res_dict' in data.keys() and 'reasoning' in data['res_dict'].keys():
                pre_decision_making_reasoning = data['res_dict']['reasoning']

            pre_screen_classification = screen_classification
            memory.add_recent_history("action", pre_action)
            memory.add_recent_history("decision_making_reasoning", pre_decision_making_reasoning)

            # For such cases with no expected response, we should define a retry limit
            logger.write(f'Decision reasoning: {pre_decision_making_reasoning}')

            # for information summary
            if use_information_summary and len(memory.get_recent_history("decision_making_reasoning", memory.max_recent_steps)) == memory.max_recent_steps:
                input = planner.information_summary_.input_map
                logger.write(f'> Information summary call...')
                images = memory.get_recent_history('image', config.event_count)
                reasonings = memory.get_recent_history('decision_making_reasoning', config.event_count)
                image_introduction = [{"path": images[event_i],"assistant": "","introduction": 'This is the {} screenshot of recent events. The description of this image: {}'.format(['first','second','third','fourth','fifth'][event_i], reasonings[event_i])} for event_i in range(config.event_count)]

                input["image_introduction"] = image_introduction
                input["previous_summarization"] = memory.get_summarization()
                input["task_description"] = task_description
                input["event_count"] = str(config.event_count)

                # >> Calling INFORMATION SUMMARY
                logger.write(f'>> Calling INFORMATION SUMMARY')

                data = planner.information_summary(input = input)
                info_summary = data['res_dict']['info_summary']
                entities_and_behaviors = data['res_dict']['entities_and_behaviors']
                logger.write(f'R: Summary: {info_summary}')
                logger.write(f'R: entities_and_behaviors: {entities_and_behaviors}')
                memory.add_summarization(info_summary)

            memory.add_recent_history("image", cur_screen_shot_path)

            # for success detection
            if use_success_detection:
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

                # >> Calling SUCCESS DETECTION
                logger.write(f'>> Calling SUCCESS DETECTION')
                data = planner.success_detection(input = input)

                success = data['res_dict']['success']
                success_reasoning = data['res_dict']['reasoning']
                success_criteria = data['res_dict']['criteria']

                memory.add_recent_history("success_detection_reasoning", success_reasoning)

                logger.write(f'Success: {success}')
                logger.write(f'Success criteria: {success_criteria}')
                logger.write(f'Success reason: {success_reasoning}')

            gm.store_skills()
            memory.save()

        except KeyboardInterrupt:
            logger.write('KeyboardInterrupt Ctrl+C detected, exiting.')
            gm.cleanup_io()
            videocapture.finish_capture()
            break

    gm.cleanup_io()
    videocapture.finish_capture()

if __name__ == '__main__':

    config.set_fixed_seed()

    # only change the input for different
    # the tempaltes are now fixed

    planner_params = {
        "__check_list__": [
            "decision_making",
            "gather_information",
            "success_detection",
            "information_summary",
            "gather_text_information"
        ],
        "prompt_paths": {
            "inputs": {
                "decision_making": "./res/prompts/inputs/decision_making.json",
                "gather_information": "./res/prompts/inputs/gather_information.json",
                "success_detection": "./res/prompts/inputs/success_detection.json",
                "self_reflection": "./res/prompts/inputs/self_reflection.json",
                "information_summary": "./res/prompts/inputs/information_summary.json",
                "gather_text_information": "./res/prompts/inputs/gather_text_information.json"
            },
            "templates": {
                "decision_making": "./res/prompts/templates/decision_making.prompt",
                "gather_information": "./res/prompts/templates/gather_information.prompt",
                "success_detection": "./res/prompts/templates/success_detection.prompt",
                "self_reflection": "./res/prompts/templates/self_reflection.prompt",
                "information_summary": "./res/prompts/templates/information_summary.prompt",
                "gather_text_information": "./res/prompts/templates/gather_text_information.prompt"
            },
        }
    }

    skill_library = ['turn', 'move_forward', 'turn_and_move_forward', 'follow', 'aim', 'shoot', 'shoot_wolves', 'select_weapon', 'select_sidearm', 'fight']
    #skill_library = move_skills + follow_skills
    #task_description =  "Follow Dutch."
    #task_description =  "Hitch your horse."
    #task_description =  "Go to the shed and press Q to take cover"
    #task_description =  "Hold right mouse to shoot"
    task_description =  ""

    # map_create_waypoint
    # skill_library = map_skills
    # task_description = "Mark the \"Saloon\" on a Map as the Waypoint via the Index."

    # buy_item
    # skill_library = trade_skills + buy_skills
    # task_description = "Your task is to buy one 'APPLE'."

    # enter the store
    # skill_library = move_skills
    # task_description =  "Your task is to enter the general store."

    # approach the shopkeeper
    # skill_library = move_skills
    # task_description =  "Your task is to approach the shopkeeper."

    #main_test_decision_making(planner_params, task_description, skill_library)

    #main_test_success_detection(planner_params, task_description)

    #main_test_information_summary(planner_params, task_description, skill_library)

    config.ocr_fully_ban = True # not use ocr
    config.ocr_enabled = False
    config.skill_retrieval = True

    main_pipeline(planner_params, task_description, skill_library, use_success_detection = False, use_self_reflection = True, use_information_summary = True)

    # skill_library_test()

    # video_path = ""
    # main_test_self_reflection(planner_params, task_description, skill_library, video_path)

    # image_path = ""
    # main_test_gather_information(image_path=image_path)

    # image_path = [
    #             ('image_path_1', '0_00_00_001'),
    #             ('image_path_2', '0_00_00_004'),
    #             ]
    # main_test_gather_information(image_path=image_path)


    #video_path = ""
    #main_test_gather_information(video_path=video_path)