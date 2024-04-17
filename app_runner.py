import os
import time
from copy import deepcopy
import argparse
from typing import Dict, Any, List
import atexit

from cradle import constants
from cradle.log import Logger
from cradle.planner.planner import Planner
from cradle.config import Config
from cradle.memory import LocalMemory
from cradle.provider.openai import OpenAIProvider
from cradle.gameio.io_env import IOEnvironment
from cradle.gameio.game_manager import GameManager
from cradle.gameio.video.VideoRecorder import VideoRecorder
from cradle.gameio.lifecycle.ui_control import switch_to_game
import cradle.environment.outlook

config = Config()
logger = Logger()
io_env = IOEnvironment()


class PipelineRunner():

    def __init__(self,
                 llm_provider_config_path: str,
                 use_success_detection: bool = False,
                 use_self_reflection: bool = False,
                 use_information_summary: bool = False):

        self.llm_provider_config_path = llm_provider_config_path

        self.use_success_detection = use_success_detection
        self.use_self_reflection = use_self_reflection
        self.use_information_summary = use_information_summary

        # Init internal params
        self.set_internal_params()


    def set_internal_params(self, *args, **kwargs):

        # Init LLM provider
        self.llm_provider = OpenAIProvider()
        self.llm_provider.init_provider(self.llm_provider_config_path)

        # Init GD provider (not used in this example)
        self.gd_detector = None

        # Init video frame extractor (not used in this example)
        self.frame_extractor = None

        # Init icon replacer
        self.icon_replacer = None

        # Init memory
        self.memory = LocalMemory(memory_path=config.work_dir,
                                  max_recent_steps=config.max_recent_steps)
        self.memory.load(config.memory_load_path)

        # Init game manager
        self.gm = GameManager(env_name=config.env_name,
                              embedding_provider=self.llm_provider)

        self.interface = self.gm.get_interface()
        self.planner_params = self.interface.planner_params
        self.skill_library = self.interface.skill_library
        self.task_description = self.interface.task_description

        # Init planner
        self.planner = Planner(llm_provider=self.llm_provider,
                               planner_params=self.planner_params,
                               frame_extractor=self.frame_extractor,
                               icon_replacer=self.icon_replacer,
                               object_detector=self.gd_detector,
                               use_self_reflection=self.use_self_reflection,
                               use_information_summary=self.use_information_summary)

        # Init skill library
        if config.skill_retrieval:
            self.gm.register_available_skills(self.skill_library)
            self.skill_library = self.gm.retrieve_skills(query_task=self.task_description,
                                                         skill_num=config.skill_num,
                                                         screen_type=constants.GENERAL_GAME_INTERFACE)
        self.skill_library = self.gm.get_skill_information(self.skill_library)

        # Init video recorder
        self.videocapture = VideoRecorder(os.path.join(config.work_dir, 'video.mp4'))


    def run(self):

        self.task_description = "Select View menu"  # "Open File menu"
        params = {}

        # Switch to target environment
        switch_to_game()

        # Prepare
        self.videocapture.start_capture()
        start_frame_id = self.videocapture.get_current_frame_id()

        cur_screenshot_path, _ = self.gm.capture_screen()
        self.memory.add_recent_history("image", cur_screenshot_path)

        success = False

        time.sleep(2)
        end_frame_id = self.videocapture.get_current_frame_id()

        params.update({
            "start_frame_id": start_frame_id,
            "end_frame_id": end_frame_id,
            "cur_screenshot_path": cur_screenshot_path,
            "exec_info": {
                "errors": False,
                "errors_info": ""
            },
            "pre_action": "",
            "pre_screen_classification": "",
            "pre_decision_making_reasoning": "",
            "pre_self_reflection_reasoning": "",
            "task_description": self.task_description,
            "summarization": "",
        })

        while not success:
            try:
                # Gather information
                gather_information_params = self.gather_information(params, debug=False)
                params.update(gather_information_params)

                # Self reflection
                self_reflection_params = self.self_reflection(params)
                params.update(self_reflection_params)

                # # Skill retrieval
                # skill_retrieval_params = self.skill_retrieval(params)
                # params.update(skill_retrieval_params)

                # Decision making
                decision_making_params = self.decision_making(params)
                params.update(decision_making_params)

                # # Information summary
                # information_summary_params = self.information_summary(params)
                # params.update(information_summary_params)

                # # Success detection
                # success_detection_params = self.success_detection(params)
                # params.update(success_detection_params)

                # success = success_detection_params["success"]

                self.gm.store_skills()
                self.memory.save()

            except KeyboardInterrupt:
                logger.write('KeyboardInterrupt Ctrl+C detected, exiting.')
                self.pipeline_shutdown()
                break

        self.pipeline_shutdown()


    def self_reflection(self, params: Dict[str, Any]):

        start_frame_id = params["start_frame_id"]
        end_frame_id = params["end_frame_id"]

        #task_description = params["task_description"]
        task_description = params["task_description"]
        pre_action = params["pre_action"]
        pre_decision_making_reasoning = params["pre_decision_making_reasoning"]
        exec_info = params["exec_info"]

        self_reflection_reasoning = ""
        if self.use_self_reflection and start_frame_id > -1:
            input = self.planner.self_reflection_.input_map
            action_frames = []
            video_frames = self.videocapture.get_frames(start_frame_id, end_frame_id)

            # if len(video_frames) <= config.max_images_in_self_reflection * config.duplicate_frames + 1:
            #     action_frames = [frame[1] for frame in video_frames[1::config.duplicate_frames]]
            # else:
            #     for i in range(config.max_images_in_self_reflection):
            #         step = len(video_frames) // config.max_images_in_self_reflection * i + 1
            #         action_frames.append(video_frames[step][1])

            # only use the first and last frame for self-reflection
            # add grid and color band to the frames
            action_frames.append(self.gm.interface.augment_image(video_frames[0][1]))
            action_frames.append(self.gm.interface.augment_image(video_frames[-1][1]))

            image_introduction = [
                {
                    "introduction": "Here are the sequential frames of the character executing the last action.",
                    "path": action_frames,
                    "assistant": "",
                    "resolution": "low"
                }]

            input["image_introduction"] = image_introduction
            input["task_description"] = task_description
            input['skill_library'] = self.skill_library
            input["previous_reasoning"] = pre_decision_making_reasoning

            if pre_action:

                pre_action_name = []
                pre_action_code = []

                skill = self.gm.skill_registry.convert_expression_to_skill(pre_action)

                name, params = skill
                action_code, action_info = self.gm.get_skill_library_in_code(name)
                pre_action_name.append(name)
                pre_action_code.append(action_code if action_code is not None else action_info)

                input["previous_action"] = ",".join(pre_action_name)
                input["previous_action_call"] = pre_action
                input['action_code'] = "\n".join(list(set(pre_action_code)))
            else:
                input["previous_action"] = ""
                input["previous_action_call"] = ""
                input['action_code'] = ""

            if exec_info["errors"]:
                input['executing_action_error'] = exec_info["errors_info"]
            else:
                input['executing_action_error'] = ""

            # >> Calling SELF REFLECTION
            logger.write(f'>> Calling SELF REFLECTION')
            reflection_data = self.planner.self_reflection(input=input)

            if 'reasoning' in reflection_data['res_dict'].keys():
                self_reflection_reasoning = reflection_data['res_dict']['reasoning']
            else:
                self_reflection_reasoning = ""

            self.memory.add_recent_history("self_reflection_reasoning", self_reflection_reasoning)
            logger.write(f'Self-reflection reason: {self_reflection_reasoning}')

        res_params = {
            "pre_self_reflection_reasoning": self_reflection_reasoning
        }

        return res_params


    def pipeline_shutdown(self):
        self.gm.cleanup_io()
        self.videocapture.finish_capture()
        logger.write('>>> Bye.')


    # def skill_retrieval(self, params: Dict[str, Any]):

    #     last_task_guidance = params["last_task_guidance"]
    #     long_horizon = params["long_horizon"]
    #     all_generated_actions = params["all_generated_actions"]
    #     screen_classification = params["screen_classification"]
    #     task_description = params["task_description"]

    #     if last_task_guidance:
    #         task_description = last_task_guidance
    #         self.memory.add_task_guidance(last_task_guidance, long_horizon)

    #     logger.write(f'Current Task Guidance: {task_description}')

    #     if config.skill_retrieval:
    #         for extracted_skills in all_generated_actions:
    #             extracted_skills = extracted_skills['values']
    #             for extracted_skill in extracted_skills:
    #                 self.gm.add_new_skill(skill_code=extracted_skill['code'])

    #         skill_library = self.gm.retrieve_skills(query_task=task_description, skill_num=config.skill_num,
    #                                                 screen_type=screen_classification.lower())
    #         logger.write(f'skill_library: {skill_library}')
    #         skill_library = self.gm.get_skill_information(skill_library)

    #     self.videocapture.clear_frame_buffer()

    #     res_params = {}
    #     return res_params


    def gather_information(self, params: Dict[str, Any], debug=False):

        # Get params
        start_frame_id = params["start_frame_id"]
        end_frame_id = params["end_frame_id"]
        cur_screenshot_path: List[str] = params["cur_screenshot_path"]

        # Gather information preparation
        logger.write(f'Gather Information Start Frame ID: {start_frame_id}, End Frame ID: {end_frame_id}')
        input = self.planner.gather_information_.input_map

        # Configure the test
        # if you want to test with a pre-defined screenshot, you can replace the cur_screenshot_path with the path to the screenshot
        pre_defined_sreenshot = None
        if pre_defined_sreenshot is not None:
            cur_screenshot_path = pre_defined_sreenshot
        else:
            cur_screenshot_path = params['cur_screenshot_path']

        # Modify the general input for gather_information here
        input["image_introduction"][0]["path"] = cur_screenshot_path

        # Configure the gather_information module
        gather_information_configurations = {
            "frame_extractor": False,  # extract text from the video clip
            "icon_replacer": False,
            "llm_description": True,  # get the description of the current screenshot
            "object_detector": False
        }
        input["gather_information_configurations"] = gather_information_configurations

        # >> Calling INFORMATION GATHERING
        logger.write(f'>> Calling INFORMATION GATHERING')

        if debug:
            # Do not call GPT-4V, just take the screenshot
            data = {
                "res_dict": {
                    "image_description": "No description",
                    "screen_classification": "None"
                }
            }
        else:
            data = self.planner.gather_information(input=input)

        response_keys = data['res_dict'].keys()

        if constants.IMAGE_DESCRIPTION in response_keys:
            image_description = data['res_dict'][constants.IMAGE_DESCRIPTION]
            if constants.SCREEN_CLASSIFICATION in response_keys:
                screen_classification = data['res_dict'][constants.SCREEN_CLASSIFICATION]
            else:
                screen_classification = "None"
        else:
            logger.warn(f"No {constants.IMAGE_DESCRIPTION} in response.")
            image_description = "No description"
            screen_classification = "None"

        self.memory.add_recent_history(key=constants.IMAGES_MEM_BUCKET, info=cur_screenshot_path)

        logger.write('Gather Information response: ', data['res_dict'])
        logger.write(f'Image Description: {image_description}')
        logger.write(f'Screen Classification: {screen_classification}')

        res_params = {
            "screen_classification": screen_classification,
            "response_keys": response_keys,
            "response": data['res_dict'],
        }

        return res_params


    def decision_making(self, params: Dict[str, Any]):

        response_keys = params["response_keys"]
        response = params["response"]
        pre_action = params["pre_action"]
        pre_self_reflection_reasoning = params["pre_self_reflection_reasoning"]
        pre_screen_classification = params["pre_screen_classification"]
        screen_classification = params["screen_classification"]

        # Decision making preparation
        input = deepcopy(self.planner.decision_making_.input_map)
        img_prompt_decision_making = self.planner.decision_making_.input_map["image_introduction"]

        number_of_execute_skills = input["number_of_execute_skills"]

        if pre_action:
            input["previous_action"] = self.memory.get_recent_history("action", k=1)[-1]
            input["previous_reasoning"] = self.memory.get_recent_history("decision_making_reasoning", k=1)[-1]

        if pre_self_reflection_reasoning:
            input["previous_self_reflection_reasoning"] = self.memory.get_recent_history("self_reflection_reasoning", k=1)[-1]

        input['skill_library'] = self.skill_library
        input['info_summary'] = self.memory.get_summarization()

        # @TODO: few shots should be REMOVED in prompt decision making
        input['few_shots'] = []

        # @TODO Temporary solution with fake augmented entries if no bounding box exists. Ideally it should read images, then check for possible augmentation.
        image_memory = self.memory.get_recent_history("image", k=config.decision_making_image_num)

        image_introduction = []
        for i in range(len(image_memory), 0, -1):
                image_introduction.append(
                    {
                        "introduction": img_prompt_decision_making[-i]["introduction"],
                        "path":image_memory[-i],
                        "assistant": img_prompt_decision_making[-i]["assistant"]
                    })

        input["image_introduction"] = image_introduction
        input["task_description"] = self.task_description

        # >> Calling DECISION MAKING
        logger.write(f'>> Calling DECISION MAKING')
        data = self.planner.decision_making(input = input)

        pre_decision_making_reasoning = ''
        if 'res_dict' in data.keys() and 'reasoning' in data['res_dict'].keys():
            pre_decision_making_reasoning = data['res_dict']['reasoning']

        # For such cases with no expected response, we should define a retry limit
        logger.write(f'Decision reasoning: {pre_decision_making_reasoning}')

        # Try to execute selected skills
        skill_steps = data['res_dict']['actions']
        if skill_steps is None:
            skill_steps = []

        logger.write(f'Response steps: {skill_steps}')

        # Filter nop actions in list
        skill_steps = [ i for i in skill_steps if i != '']
        if len(skill_steps) == 0:
            skill_steps = ['']

        skill_steps = skill_steps[:number_of_execute_skills]
        logger.write(f'Skill Steps: {skill_steps}')

        start_frame_id = self.videocapture.get_current_frame_id()

        exec_info = self.gm.execute_actions(skill_steps)

        cur_screenshot_path, _ = self.gm.capture_screen(draw_mouse=True)

        end_frame_id = self.videocapture.get_current_frame_id()

        # exec_info also has the list of successfully executed skills. skill_steps is the full list, which may differ if there were execution errors.
        pre_action = exec_info["last_skill"]

        pre_screen_classification = screen_classification
        self.memory.add_recent_history("action", pre_action)
        self.memory.add_recent_history("decision_making_reasoning", pre_decision_making_reasoning)

        res_params = {
            "pre_action": pre_action,
            "pre_decision_making_reasoning": pre_decision_making_reasoning,
            "pre_screen_classification": pre_screen_classification,
            "exec_info": exec_info,
            "start_frame_id": start_frame_id,
            "end_frame_id": end_frame_id,
            "cur_screenshot_path": cur_screenshot_path,
        }

        return res_params


    # def information_summary(self, params: Dict[str, Any]):

    #     task_description = params["task_description"]
    #     cur_screenshot_path = params["cur_screenshot_path"]

    #     # Information summary preparation
    #     if (self.use_information_summary and len(self.memory.get_recent_history("decision_making_reasoning",
    #              self.memory.max_recent_steps)) == self.memory.max_recent_steps):

    #         input = self.planner.information_summary_.input_map
    #         logger.write(f'> Information summary call...')

    #         images = self.memory.get_recent_history('image', config.event_count)
    #         reasonings = self.memory.get_recent_history('decision_making_reasoning', config.event_count)

    #         image_introduction = [
    #             {
    #                 "path": images[event_i], "assistant": "",
    #                 "introduction": 'This is the {} screenshot of recent events. The description of this image: {}'.format(
    #                     ['first', 'second', 'third', 'fourth', 'fifth'][event_i], reasonings[event_i])
    #             } for event_i in range(config.event_count)
    #         ]

    #         input["image_introduction"] = image_introduction
    #         input["previous_summarization"] = self.memory.get_summarization()
    #         input["task_description"] = task_description
    #         input["event_count"] = str(config.event_count)

    #         # >> Calling INFORMATION SUMMARY
    #         logger.write(f'>> Calling INFORMATION SUMMARY')

    #         data = self.planner.information_summary(input=input)
    #         info_summary = data['res_dict']['info_summary']
    #         entities_and_behaviors = data['res_dict']['entities_and_behaviors']
    #         logger.write(f'R: Summary: {info_summary}')
    #         logger.write(f'R: entities_and_behaviors: {entities_and_behaviors}')
    #         self.memory.add_summarization(info_summary)

    #     self.memory.add_recent_history("image", cur_screenshot_path)

    #     res_params = {}
    #     return res_params


    # def success_detection(self, params: Dict[str, Any]):

    #     task_description = params["task_description"]

    #     success = False
    #     success_reasoning = ""
    #     success_criteria = ""

    #     # Success detection preparation
    #     if self.use_success_detection:
    #         input = self.planner.success_detection_.input_map
    #         image_introduction = [
    #             {
    #                 "introduction": input["image_introduction"][-2]["introduction"],
    #                 "path": self.memory.get_recent_history("image", k=2)[0],
    #                 "assistant": input["image_introduction"][-2]["assistant"]
    #             },
    #             {
    #                 "introduction": input["image_introduction"][-1]["introduction"],
    #                 "path": self.memory.get_recent_history("image", k=1)[0],
    #                 "assistant": input["image_introduction"][-1]["assistant"]
    #             }
    #         ]
    #         input["image_introduction"] = image_introduction

    #         input["task_description"] = task_description
    #         input["previous_action"] = self.memory.get_recent_history("action", k=1)[-1]
    #         input["previous_reasoning"] = self.memory.get_recent_history("decision_making_reasoning", k=1)[-1]

    #         # >> Calling SUCCESS DETECTION
    #         logger.write(f'>> Calling SUCCESS DETECTION')
    #         data = self.planner.success_detection(input=input)

    #         success = data['res_dict']['success']
    #         success_reasoning = data['res_dict']['reasoning']
    #         success_criteria = data['res_dict']['criteria']

    #         self.memory.add_recent_history("success_detection_reasoning", success_reasoning)

    #         logger.write(f'Success: {success}')
    #         logger.write(f'Success criteria: {success_criteria}')
    #         logger.write(f'Success reason: {success_reasoning}')

    #     res_params = {
    #         "success": success,
    #         "success_reasoning": success_reasoning,
    #         "success_criteria": success_criteria
    #     }
    #     return res_params


def exit_cleanup(runner):
    logger.write("Exiting pipeline.")
    runner.pipeline_shutdown()


def get_args_parser():

    parser = argparse.ArgumentParser("Cradle Prototype Runner")
    parser.add_argument("--providerConfig", type=str, default="./conf/openai_config.json", help="The path to the provider config file")
    parser.add_argument("--envConfig", type=str, default="./conf/env_config_outlook.json", help="The path to the environment config file")
    return parser


def main(args):

    config.load_env_config(args.envConfig)
    config.set_fixed_seed()

    config.ocr_fully_ban = True # not use local OCR-checks
    config.ocr_enabled = False
    config.skill_retrieval = True
    config.skill_from_local = True

    pipelineRunner = PipelineRunner(args.providerConfig,
                                    use_success_detection = False,
                                    use_self_reflection = True,
                                    use_information_summary = False)

    atexit.register(exit_cleanup, pipelineRunner)

    pipelineRunner.run()


if __name__ == '__main__':

    args = get_args_parser()
    args = args.parse_args()
    main(args)