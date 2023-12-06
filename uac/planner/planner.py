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
                            InformationSummaryInput,
                            InformationSummaryOutput)
from uac.provider.base_llm import LLMProvider
from uac.utils.check import check_planner_params
from uac.utils.json_utils import load_json, parse_semi_formatted_json
from uac.utils.file_utils import assemble_project_path, read_resource_file

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

        # Get the current screen classification
        flag = True
        class_ = None
        try:
            image = deepcopy(screenshot_file)
            screen_classification_input = ScreenClassificationInput(params=input)
            content = screen_classification_input.to_text(template_str=self.template["template"])

            # Call the LLM provider for screen classification json
            response, info = self.llm_provider(content=content, image=image)

            # Convert the response to dict
            processed_response = parse_semi_formatted_json(response)

            # convert the dict to ScreenClassificationOutput
            screen_classification_output = ScreenClassificationOutput(params=processed_response)

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

    def _pre(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return input

    def __call__(self, *args, input: Dict[str, Any] = None, class_ = None, **kwargs) -> Dict[str, Any]:

        input = self.input_map if input is None else input
        input = self._pre(input=input)

        image_files = []
        if "image_introduction" in input.keys():
            for image_info in input["image_introduction"]:
                image_files.append(image_info["path"])

        flag = True

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
            message_prompts = self.llm_provider.assemble_prompt(self.system_prompts[0], self.template, input)

            logger.debug(f'>> Upstream - R: {message_prompts}')

            response, info = self.llm_provider.create_completion(message_prompts)

            logger.debug(f'>> Downstream - A: {response}')

            # Convert the response to dict
            processed_response = parse_semi_formatted_json(response)

            # Convert the dict to GatherInformationOutput
            logger.debug(f'GI response type was {processed_response["type"]}')
            processed_response["type"] = "gather_information" # @TODO HACK
            llm_provider_gather_information_output = GatherInformationOutput(params=processed_response)

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
            processed_response["objects"] = objects

            # res_json = json.dumps(llm_provider_gather_information_output, default=json_encoder, indent=4)

        success = self._check_success(data = processed_response)

        data = dict(
            flag = flag,
            success = success,
            input = input,
            res_dict = processed_response,
            # res_json = res_json
        )

        data = self._post(data = data)

        return data


    def _post(self, *args, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return data

    def _check_success(self, *args, data, **kwargs):

        success = False

        prop_name = "description"

        if prop_name in data.keys():
            desc = data[prop_name]
            success = desc is not None and len(desc) > 0
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

    def _pre(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return input

    def __call__(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        input = self.input_map if input is None else input
        input = self._pre(input=input)

        flag = True
        outcome = None
        processed_response = {}

        try:

            decision_making_input = DecisionMakingInput(params=input)

            message_prompts = self.llm_provider.assemble_prompt(system_prompt=self.system_prompts[0], template_str=self.template, params=input)

            logger.debug(f'>> Upstream - R: {message_prompts}')

            # Call the LLM provider for decision making
            response, info = self.llm_provider.create_completion(message_prompts)

            logger.debug(f'>> Downstream - A: {response}')

            if response is None or len(response) == 0:
                logger.warn('No response in decision making call')
                logger.debug(input)

            # Convert the response to dict
            processed_response = parse_semi_formatted_json(response)

            # Convert the dict to DecisionmakingOutput
            decision_making_output = DecisionMakingOutput(params=processed_response)

            outcome = decision_making_output.skill_steps

            # res_json = json.dumps(decision_making_output, default=json_encoder, indent=4)

        except Exception as e:
            logger.error(f"Error in decision_making: {e}")
            logger.error_ex(e)
            flag = False

        data = dict(
            flag = flag,
            input = input,
            # res_json = res_json,
            res_dict = processed_response,
            outcome = outcome,
        )

        data = self._post(data = data)
        return data

    def _post(self, *args, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return data


class SuccessDetection():
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

    def _pre(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return input

    def __call__(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        input = self.input_map if input is None else input
        input = self._pre(input=input)

        flag = True
        processed_response = {}
        outcome = None

        try:

            # Call the LLM provider for success detection
            success_detection_input = SuccessDetectionInput(params=input)

            message_prompts = self.llm_provider.assemble_prompt(system_prompt=self.system_prompts[0], template_str=self.template, params=input)

            logger.debug(f'>> Upstream - R: {message_prompts}')

            response, info = self.llm_provider.create_completion(message_prompts)

            logger.debug(f'>> Downstream - A: {response}')

            # Convert the response to dict
            processed_response = parse_semi_formatted_json(response)

            # Convert the dict to SuccessDetectionOutput
            success_detection_output = SuccessDetectionOutput(params=processed_response)

            outcome = success_detection_output.succcess

            # res_json = json.dumps(success_detection_output, default=json_encoder, indent=4)

        except Exception as e:
            logger.error(f"Error in success_detection: {e}")
            flag = False

        data = dict(
            flag=flag,
            input=input,
            # res_json=res_json,
            res_dict=processed_response,
            outcome=outcome,
        )

        data = self._post(data=data)
        return data

    def _post(self, *args, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return data

class InformationSummary():
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

    def _pre(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return input

    def __call__(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        input = self.input_map if input is None else input
        input = self._pre(input=input)

        flag = True
        processed_response = {}
        outcome = None

        try:

            # Call the LLM provider for information summary
            information_summary_input = InformationSummaryInput(params=input)

            message_prompts = self.llm_provider.assemble_prompt(system_prompt=self.system_prompts[0], template_str=self.template, params=input)

            logger.debug(f'>> Upstream - R: {message_prompts}')

            response, info = self.llm_provider.create_completion(message_prompts)

            logger.debug(f'>> Downstream - A: {response}')

            # Convert the response to dict
            processed_response = parse_semi_formatted_json(response)

            # Convert the dict to InformationSummaryOutput
            information_summary_output = InformationSummaryOutput(params=processed_response)

            outcome = information_summary_output.info_summary

            # res_json = json.dumps(information_summary_output, default=json_encoder, indent=4)

        except Exception as e:
            logger.error(f"Error in information_summary: {e}")
            flag = False

        data = dict(
            flag=flag,
            input=input,
            # res_json=res_json,
            res_dict=processed_response,
            outcome=outcome,
        )

        data = self._post(data=data)
        return data

    def _post(self, *args, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
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

        self.system_prompts = system_prompts
        self.llm_provider = llm_provider

        self.use_screen_classification = use_screen_classification
        self.gather_information_max_steps = gather_information_max_steps

        self.marker_matcher = marker_matcher
        self.object_detector = object_detector

        self.set_internal_params(planner_params, use_screen_classification)


    # Allow re-configuring planner
    def set_internal_params(self, planner_params: Dict = None, use_screen_classification: bool = False):

        self.planner_params = planner_params

        if not check_planner_params(self.planner_params):
            raise ValueError(f"Error in planner_params: {self.planner_params}")

        self.input_examples = self._init_input_example()
        self.templates = self._init_template()
        self.output_examples = self._init_output_example()

        if use_screen_classification:
            self.screen_classification_ = ScreenClassification(self.system_prompts,
                                                               self.input_examples["screen_classification"],
                                                               self.templates["screen_classification"],
                                                               self.output_examples["screen_classification"],
                                                               self.llm_provider)
        else:
            self.screen_classification_ = None
            
        self.gather_information_ = GatherInformation(self.system_prompts,
                                                     self.input_examples["gather_information"],
                                                     self.templates["gather_information"],
                                                     self.output_examples["gather_information"],
                                                     self.marker_matcher,
                                                     self.object_detector,
                                                     self.llm_provider)
        
        self.decision_making_ = DecisionMaking(self.system_prompts,
                                               self.input_examples["decision_making"],
                                               self.templates["decision_making"],
                                               self.output_examples["decision_making"],
                                               self.llm_provider)
        
        self.success_detection_ = SuccessDetection(self.system_prompts,
                                                   self.input_examples["success_detection"],
                                                   self.templates["success_detection"],
                                                   self.output_examples["success_detection"],
                                                   self.llm_provider)

        self.information_summary_ = InformationSummary(self.system_prompts,
                                                  self.input_examples["information_summary"],
                                                  self.templates["information_summary"],
                                                  self.output_examples["information_summary"],
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
        template_paths = prompt_paths["templates"]
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
      
    def gather_information(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        if input is None:
            input = self.input_examples["gather_information"]

        image_file = input["image_introduction"][0]["path"]

        if self.use_screen_classification:
            class_ = self.screen_classification_(screenshot_file=image_file)["class_"]
        else:
            class_ = None

        for i in range(self.gather_information_max_steps):
            data = self.gather_information_(input=input, class_=class_)

            success = data["success"]

            if success:
                break

        return data

    def decision_making(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        if input is None:
            input = self.input_examples["decision_making"]

        data = self.decision_making_(input=input)

        return data

    def success_detection(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        if input is None:
            input = self.input_examples["success_detection"]

        data = self.success_detection_(input=input)

        return data

    def information_summary(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        if input is None:
            input = self.input_examples["information_summary"]

        data = self.information_summary_(input=input)

        return data
