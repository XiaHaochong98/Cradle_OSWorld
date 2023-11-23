import json
from typing import Dict, Any, List
from copy import deepcopy

from uac.config import Config
from uac.log import Logger
from uac.planner.base import BasePlanner
from uac.agent.data import (ScreenClassificationInput,
                            GatherInformationInput,
                            GatherInformationOutput,
                            ScreenClassificationOutput,
                            DecisionMakingInput,
                            DecisionMakingOutput,
                            SuccessDetectionInput,
                            SuccessDetectionOutput,
                            json_encoder,
                            json_decoder)
from uac.provider.base_llm import LLMProvider
from uac.utils.check import check_planner_params
from uac.utils.json_utils import load_json
from uac.utils.file_utils import assemble_project_path, read_resource_file
from uac.provider.openai import encode_image

config = Config()
logger = Logger()

PROMPT_EXT = ".prompt"
JSON_EXT = ".json"


class ScreenClassification():
    def __init__(self,
                 system_prompt : str = None,
                 input_example: Dict = None,
                 template: Dict = None,
                 output_example: Dict = None,
                 llm_provider: LLMProvider = None,
                ):

        self.system_prompt = system_prompt
        self.input_example = input_example
        self.template = template
        self.output_example = output_example
        self.llm_provider = llm_provider

    def _pre(self, *args, input = None, screenshot_file = None, **kwargs):
        return input, screenshot_file

    def __call__(self, *args, input = None, screenshot_file = None, **kwargs):

        input = self.input_example if input is None else input
        input = self._pre(input=input, screenshot_file=screenshot_file)

        # get the current screen classification
        flag = True
        class_ = None
        try:
            image = deepcopy(screenshot_file)
            screen_classification_input = ScreenClassificationInput(params=input)
            content = screen_classification_input.to_text(template_str=self.template["template"])

            # call the LLM provider for screen classification json
            response_json = self.llm_provider(content=content, image=image).json()

            # convert the json to dict
            response_dict = json.loads(response_json)

            # convert the dict to ScreenClassificationOutput
            screen_classification_output = ScreenClassificationOutput(params=response_dict)

            # get the screen class_
            class_ = screen_classification_output.class_

            assert class_ in self.input_example["classes"], f"Error in class_: {class_}"

        except Exception as e:
            logger.error(f"Error in gather_information: {e}")
            flag = False

        data = dict(
            flag = flag,
            input = input,
            screenshot_file = screenshot_file,
            class_= class_,
        )
        data = self._post(data = data)
        return data

    def _post(self, *args, data = None, **kwargs):
        return data

class GatherInformation():

    def __init__(self,
                 system_prompts: List[str] = None,
                 input_map: Dict = None,
                 template: str = None,
                 output_example: Dict = None,
                 marker_matcher: Any = None,
                 object_detector: Any = None,
                 llm_provider: LLMProvider = None,
                ):

        self.system_prompts = system_prompts
        self.input_map = input_map
        self.template = template
        self.output_example = output_example
        self.marker_matcher = marker_matcher
        self.object_detector = object_detector
        self.llm_provider = llm_provider

    def _pre(self, *args, input = None, image_files = None, **kwargs):
        return input, image_files

    def __call__(self, *args, input: Dict = None, image_files: List[str] = None, class_ = None, **kwargs):

        input = self.input_map if input is None else input
        input = self._pre(input=input, image_files=image_files)

        flag = True
        res_json = None

        marker_matcher_gathered_information_output = None
        object_detector_gathered_information_output = None
        llm_provider_gather_information_output = None

        # Gather information by marker matcher
        if self.marker_matcher is not None:
            try:
                marker_matcher_gathered_information = self.marker_matcher(screenshot_file=image_files[0], class_=class_)
                marker_matcher_gathered_information_output = GatherInformationOutput(params=marker_matcher_gathered_information)
            except Exception as e:
                logger.error(f"Error in gather information by marker matcher: {e}")
                flag = False

        # Gather information by object detector
        if self.object_detector is not None:        
            try:
                object_detector_gathered_information = self.object_detector(screenshot_file=image_files[0], class_=class_)
                object_detector_gathered_information_output = GatherInformationOutput(params=object_detector_gathered_information)
            except Exception as e:
                logger.error(f"Error in gather information by object detector: {e}")
                flag = False

        # Gather information by LLM provider - mandatory
        try:
            if image_files is not None:
                image_files = [assemble_project_path(image_path) for image_path in image_files]

            gather_information_input = GatherInformationInput(params=input)
            user_content = gather_information_input.to_text(self.template, input)

            # Call the LLM provider for gather information json
            message_prompts = self.llm_provider.assemble_prompt(self.system_prompts, [user_content], image_files)

            logger.write(f'U: {message_prompts}')

            response = self.llm_provider.create_completion(message_prompts)[0]

            logger.write(f'A: {response}')

            # @TODO Change to return as json
            response_dict = dict()
            response_dict["type"] = "gather_information"
            response_dict["description"] = response

            # Convert the json to dict
            #response_dict = json.loads(response_json)

            # Convert the dict to GatherInformationOutput
            llm_provider_gather_information_output = GatherInformationOutput(params=response_dict)

        except Exception as e:
            logger.error(f"Error in gather_information: {e}")
            flag = False

        if flag:
            objects = []

            if marker_matcher_gathered_information_output is not None:
                objects.extend(marker_matcher_gathered_information_output.objects)
            if object_detector_gathered_information_output is not None:
                objects.extend(object_detector_gathered_information_output.objects)
            if llm_provider_gather_information_output is not None:
                objects.extend(llm_provider_gather_information_output.objects)

            objects = list(set(objects))

            llm_provider_gather_information_output.objects = objects

            res_json = json.dumps(llm_provider_gather_information_output, default=json_encoder, indent=4)

        success = self._check_success(res_json=res_json)

        data = dict(
            flag = flag,
            success = success,
            input = input,
            image_files = image_files,
            res_json = res_json
        )

        data = self._post(data = data)

        return data


    def _post(self, *args, data = None, **kwargs):
        return data

    def _check_success(self, *args, res_json, **kwargs):
        success = "\"description\"" in res_json
        return success


class DecisionMaking():
    def __init__(self,
                 system_prompts: List[str] = None,
                 input_map: Dict = None,
                 template: Dict = None,
                 output_example: Dict = None,
                 llm_provider: LLMProvider = None,
                ):

        self.system_prompts = system_prompts
        self.input_map = input_map
        self.template = template
        self.output_example = output_example
        self.llm_provider = llm_provider

    def _pre(self, *args, input = None, image_files = None, **kwargs):
        return input, image_files

    def __call__(self, *args, input = None, image_files: List[str] = None, **kwargs):

        input = self.input_map if input is None else input
        input = self._pre(input=input, image_files=image_files)

        flag = True
        try:
            if image_files is not None:
                image_files = [assemble_project_path(image_path) for image_path in image_files]

            decision_making_input = DecisionMakingInput(params=input)
            user_content = decision_making_input.to_text(self.template, input)

            # call the LLM provider for decision making json
            message_prompts = self.llm_provider.assemble_prompt(self.system_prompts, [user_content], image_files)

            logger.write(f'U: {message_prompts}')

            response = self.llm_provider.create_completion(message_prompts)[0]

            logger.write(f'A: {response}')

            # @TODO better cleanup formatting
            response_json = response.replace("```json\n", "").replace("json```\n", "").replace("```", "").replace("\n", "").replace("\'", "")

            # convert the json to dict
            response_dict = json.loads(response_json)

            # convert the dict to DecisionmakingOutput
            decision_making_output = DecisionMakingOutput(params=response_dict)

        except Exception as e:
            logger.error(f"Error in decision_making: {e}")
            flag = False

        res_json = json.dumps(decision_making_output, default=json_encoder, indent=4)

        data = dict(
            flag = flag,
            input = input,
            image_files = image_files,
            res_json = res_json
        )

        data = self._post(data = data)
        return data

    def _post(self, *args, data = None, **kwargs):
        return data


class SuccessDetection():
    def __init__(self,
                 system_prompts: List[str] = None,
                 input_example: Dict = None,
                 template: Dict = None,
                 output_example: Dict = None,
                 llm_provider: LLMProvider = None,
                ):

        self.system_prompts = system_prompts
        self.input_example = input_example
        self.template = template
        self.output_example = output_example
        self.llm_provider = llm_provider

    def _pre(self, *args, input = None, image_files = None, **kwargs):
        return input, image_files

    def __call__(self, *args, input = None, image_files: List[str] = None, **kwargs):

        input = self.input_example if input is None else input
        input = self._pre(input=input, image_files=image_files)

        flag = True
        success = None
        try:

            # @TODO: Improve handling of multiple images and positioning in conversation
            if image_files is not None:
                image_files = [assemble_project_path(image_path) for image_path in image_files]

            # Call the LLM provider for success detection
            success_detection_input = SuccessDetectionInput(params=input)
            user_content = success_detection_input.to_text(self.template, input)

            message_prompts = self.llm_provider.assemble_prompt(self.system_prompts, [user_content], image_files)

            logger.write(f'U: {message_prompts}')

            response = self.llm_provider.create_completion(message_prompts)[0]

            logger.write(f'A: {response}')

            # @TODO better cleanup formatting
            response_json = response.replace("```json\n", "").replace("json```\n", "").replace("```", "").replace("\n", "").replace("\'", "")

            # Convert the json to dict
            response_dict = json.loads(response_json)

            # Convert the dict to SuccessDetectionOutput
            success_detection_output = SuccessDetectionOutput(params=response_dict)

            outcome = success_detection_output.decision

        except Exception as e:
            logger.error(f"Error in success_detection: {e}")
            flag = False

        data = dict(
            flag = flag,
            input = input,
            image_files = image_files,
            outcome = outcome
        )

        data = self._post(data = data)
        return data

    def _post(self, *args, data = None, **kwargs):
        return data


class Planner(BasePlanner):
    def __init__(self,
                 llm_provider: Any = None,
                 system_prompts: List[str] = None,
                 planner_params: Dict = None,
                 use_screen_classification: bool = False,
                 gather_information_max_steps: int = 1, # 5,
                 marker_matcher: Any = None,
                 object_detector: Any = None,
                 **kwargs,
                 ):

        """
        input example: Sample of data entered into the LLM provider
        template: Template for input data to the LLM provider, splicing the input example into a single sentence message
        output_example: Output data from the LLM provider

        planner_params = {
            "__check_list__":[
              "screen_classification",
              "gather_information",
              "decision_making"
            ],
            "prompt_paths": {
              "input_example": {
                "screen_classification": "./res/prompts/gather_information/input_example/screen_classification.json",
                "gather_information": "./res/prompts/gather_information/input_example/gather_information.json",
                "decision_making": "./res/prompts/decision_making/input_example/decision_making.json"
              },
              "template": {
                "screen_classification": "./res/prompts/gather_information/template/screen_classification.json",
                "gather_information": "./res/prompts/gather_information/template/gather_information.json",
                "decision_making": "./res/prompts/decision_making/template/decision_making.json"
              },
              "output_example": {
                "screen_classification": "./res/prompts/gather_information/output_example/screen_classification.json",
                "gather_information": "./res/prompts/gather_information/output_example/gather_information.json",
                "decision_making": "./res/prompts/decision_making/output_example/decision_making.json"
              }
            }
          }
        """

        super(BasePlanner, self).__init__()

        self.planner_params = planner_params
        self.system_prompts = system_prompts

        self.use_screen_classification = use_screen_classification
        self.gather_information_max_steps = gather_information_max_steps

        self.llm_provider = llm_provider
        self.marker_matcher = marker_matcher
        self.object_detector = object_detector

        if not check_planner_params(self.planner_params):
            raise ValueError(f"Error in planner_params: {self.planner_params}")

        self.input_examples = self._init_input_example()
        self.templates = self._init_template()
        self.output_examples = self._init_output_example()

        if use_screen_classification:
            self.screen_classification = ScreenClassification(self.system_prompts,
                                                              self.input_examples["screen_classification"],
                                                              self.templates["screen_classification"],
                                                              self.output_examples["screen_classification"],
                                                              self.llm_provider)
            
        self.gather_information = GatherInformation(self.system_prompts,
                                                    self.input_examples["gather_information"],
                                                    self.templates["gather_information"],
                                                    self.output_examples["gather_information"],
                                                    self.marker_matcher,
                                                    self.object_detector,
                                                    self.llm_provider)
        
        self.decision_making = DecisionMaking(self.system_prompts,
                                              self.input_examples["decision_making"],
                                              self.templates["decision_making"],
                                              self.output_examples["decision_making"],
                                              self.llm_provider)
        
        self.success_detection = SuccessDetection(self.system_prompts,
                                                  self.input_examples["success_detection"],
                                                  self.templates["success_detection"],
                                                  self.output_examples["success_detection"],
                                                  self.llm_provider)


    def _init_input_example(self):
        input_examples = dict()
        prompt_paths = self.planner_params["prompt_paths"]
        input_example_paths = prompt_paths["input_example"]
        for key, value in input_example_paths.items():
            path = assemble_project_path(value)
            if path.endswith(PROMPT_EXT):
                input_examples[key] = read_resource_file(path)
            else:
                input_examples[key] = load_json(path)
        return input_examples

    def _init_template(self):
        templates = dict()
        prompt_paths = self.planner_params["prompt_paths"]
        template_paths = prompt_paths["template"]
        for key, value in template_paths.items():
            path = assemble_project_path(value)
            if path.endswith(PROMPT_EXT):
                templates[key] = read_resource_file(path)
            else:
                templates[key] = load_json(path)
        return templates

    def _init_output_example(self):
        output_examples = dict()
        prompt_paths = self.planner_params["prompt_paths"]
        output_example_paths = prompt_paths["output_example"]
        for key, value in output_example_paths.items():
            path = assemble_project_path(value)
            if path.endswith(PROMPT_EXT):
                output_examples[key] = read_resource_file(path)
            else:
                output_examples[key] = load_json(path)
        return output_examples
      
    def _gather_information(self, *args, image_files, **kwargs):

        input = self.input_examples["gather_information"]
        if self.use_screen_classification:
            class_ = self.screen_classification(screenshot_file=image_files[0])["class_"]
        else:
            class_ = None

        for i in range(self.gather_information_max_steps):
            data = self.gather_information(input=input, image_files=image_files, class_=class_)

            success = data["success"]

            if success:
                break

            # next input and screenshot_file
            #input = data["input"]
            #screenshot_file = data["screenshot_file"]

        res_json = data["res_json"]
        return res_json

    def _decision_making(self, *args, input=None, image_files, **kwargs):

        if input is None:
            input = self.input_examples["decision_making"]

        data = self.decision_making(input=input, image_files=image_files)

        res_json = data["res_json"]
        return res_json

    def _success_detection(self, *args, input=None, image_files, **kwargs):

        data = self.success_detection(input=input, image_files=image_files)

        success = data["outcome"]
        return success
