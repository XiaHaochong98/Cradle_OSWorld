import json
from typing import Dict, Any, List
from copy import deepcopy

from uac.config import Config
from uac.log import Logger
from uac.planner.base import BasePlanner
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
                 input_example: Dict = None,
                 template: Dict = None,
                 llm_provider: LLMProvider = None,
                ):
        self.input_example = input_example
        self.template = template
        self.llm_provider = llm_provider

    def _pre(self, *args, input = None, screenshot_file = None, **kwargs):
        return input, screenshot_file

    def __call__(self, *args, input = None, screenshot_file = None, **kwargs):

        raise NotImplementedError('ScreenClassification is not implemented yet')

        # input = self.input_example if input is None else input
        # input = self._pre(input=input, screenshot_file=screenshot_file)
        #
        # # Get the current screen classification
        # flag = True
        # class_ = None
        # try:
        #     image = deepcopy(screenshot_file)
        #     screen_classification_input = ScreenClassificationInput(params=input)
        #     content = screen_classification_input.to_text(template_str=self.template["template"])
        #
        #     # Call the LLM provider for screen classification json
        #     response, info = self.llm_provider(content=content, image=image)
        #
        #     # Convert the response to dict
        #     processed_response = parse_semi_formatted_json(response)
        #
        #     # convert the dict to ScreenClassificationOutput
        #     screen_classification_output = ScreenClassificationOutput(params=processed_response)
        #
        #     # get the screen class_
        #     class_ = screen_classification_output.class_
        #
        #     assert class_ in self.input_example["classes"], f"Error in class_: {class_}"
        #
        # except Exception as e:
        #     logger.error(f"Error in gather_information: {e}")
        #     flag = False
        #
        # data = dict(
        #     flag = flag,
        #     input = input,
        #     screenshot_file = screenshot_file,
        #     class_= class_,
        # )
        #
        # data = self._post(data = data)
        # return data

    def _post(self, *args, data = None, **kwargs):
        return data


class GatherInformation():

    def __init__(self,
                 input_map: Dict = None,
                 template: str = None,
                 marker_matcher: Any = None,
                 object_detector: Any = None,
                 llm_provider: LLMProvider = None,
                ):

        self.input_map = input_map
        self.template = template
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

        marker_matcher_gathered_information = None
        object_detector_gathered_information = None
        llm_provider_gather_information = None

        processed_response = {}
        res_json = None

        # Gather information by marker matcher
        if self.marker_matcher is not None:
            try:
                marker_matcher_gathered_information = self.marker_matcher(screenshot_file=image_files[0], class_=class_)
            except Exception as e:
                logger.error(f"Error in gather information by marker matcher: {e}")
                flag = False

        # Gather information by object detector
        if self.object_detector is not None:
            try:
                object_detector_gathered_information = self.object_detector(screenshot_file=image_files[0], class_=class_)

            except Exception as e:
                logger.error(f"Error in gather information by object detector: {e}")
                flag = False

        # Gather information by LLM provider - mandatory
        try:

            # Call the LLM provider for gather information json
            message_prompts = self.llm_provider.assemble_prompt(template_str=self.template, params=input)

            logger.debug(f'>> Upstream - R: {message_prompts}')

            response, info = self.llm_provider.create_completion(message_prompts)

            logger.debug(f'>> Downstream - A: {response}')

            # Convert the response to dict
            processed_response = parse_semi_formatted_json(response)

            # Convert the dict to GatherInformationOutput
            logger.debug(f'GI response type was {processed_response["type"]}')

            llm_provider_gather_information = processed_response

        except Exception as e:
            logger.error(f"Error in gather_information: {e}")
            flag = False

        if flag:
            objects = []

            if marker_matcher_gathered_information is not None and "objects" in marker_matcher_gathered_information:
                objects.extend(marker_matcher_gathered_information["objects"])
            if object_detector_gathered_information is not None and "objects" in object_detector_gathered_information:
                objects.extend(object_detector_gathered_information["objects"])
            if llm_provider_gather_information is not None and "objects" in llm_provider_gather_information:
                objects.extend(llm_provider_gather_information["objects"])

            objects = list(set(objects))

            llm_provider_gather_information["objects"] = objects
            processed_response["objects"] = objects

            res_dict = processed_response

            # res_json = json.dumps(processed_response, indent=4)

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
                 input_map: Dict = None,
                 template: Dict = None,
                 llm_provider: LLMProvider = None,
                ):

        self.input_map = input_map
        self.template = template
        self.llm_provider = llm_provider

    def _pre(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return input

    def __call__(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        input = self.input_map if input is None else input
        input = self._pre(input=input)

        flag = True
        outcome = None
        processed_response = {}
        # res_json = None

        try:
            message_prompts = self.llm_provider.assemble_prompt(template_str=self.template,
                                                                params=input)

            logger.debug(f'>> Upstream - R: {message_prompts}')

            # Call the LLM provider for decision making
            response, info = self.llm_provider.create_completion(message_prompts)

            logger.debug(f'>> Downstream - A: {response}')

            if response is None or len(response) == 0:
                logger.warn('No response in decision making call')
                logger.debug(input)

            # Convert the response to dict
            processed_response = parse_semi_formatted_json(response)

            # res_json = json.dumps(processed_response, indent=4)

            outcome =processed_response["skill_steps"]

        except Exception as e:
            logger.error(f"Error in decision_making: {e}")
            logger.error_ex(e)
            flag = False

        data = dict(
            flag = flag,
            input = input,
            res_dict = processed_response,
            # res_json = res_json,
            outcome = outcome,
        )

        data = self._post(data = data)
        return data

    def _post(self, *args, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return data


class SuccessDetection():
    def __init__(self,
                 input_map: Dict = None,
                 template: Dict = None,
                 llm_provider: LLMProvider = None,
                ):
        self.input_map = input_map
        self.template = template
        self.llm_provider = llm_provider

    def _pre(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return input

    def __call__(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        input = self.input_map if input is None else input
        input = self._pre(input=input)

        flag = True
        processed_response = {}
        outcome = None
        # res_json = None

        try:

            # Call the LLM provider for success detection
            message_prompts = self.llm_provider.assemble_prompt(template_str=self.template, params=input)

            logger.debug(f'>> Upstream - R: {message_prompts}')

            response, info = self.llm_provider.create_completion(message_prompts)

            logger.debug(f'>> Downstream - A: {response}')

            # Convert the response to dict
            processed_response = parse_semi_formatted_json(response)

            outcome = processed_response["decision"]["success"]

            # res_json = json.dumps(processed_response, indent=4)

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
                 input_map: Dict = None,
                 template: Dict = None,
                 llm_provider: LLMProvider = None,
                ):

        self.input_map = input_map
        self.template = template
        self.llm_provider = llm_provider

    def _pre(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return input

    def __call__(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        input = self.input_map if input is None else input
        input = self._pre(input=input)

        flag = True
        processed_response = {}
        outcome = None
        res_json = None

        try:

            # Call the LLM provider for information summary
            message_prompts = self.llm_provider.assemble_prompt(template_str=self.template, params=input)

            logger.debug(f'>> Upstream - R: {message_prompts}')

            response, info = self.llm_provider.create_completion(message_prompts)

            logger.debug(f'>> Downstream - A: {response}')

            # Convert the response to dict
            processed_response = parse_semi_formatted_json(response)

            # res_json = json.dumps(processed_response, indent=4)

            outcome = processed_response["info_summary"]

        except Exception as e:
            logger.error(f"Error in information_summary: {e}")
            flag = False

        data = dict(
            flag=flag,
            input=input,
            res_dict=processed_response,
            # res_json=res_json,
            outcome=outcome,
        )

        data = self._post(data=data)
        return data

    def _post(self, *args, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return data
    
class Planner(BasePlanner):
    def __init__(self,
                 llm_provider: Any = None,
                 planner_params: Dict = None,
                 use_screen_classification: bool = False,
                 use_information_summary: bool = False,
                 gather_information_max_steps: int = 1, # 5,
                 marker_matcher: Any = None,
                 object_detector: Any = None,
                 ):
        """
        inputs: input key-value pairs
        templates: template for composing the prompt

        planner_params = {
            "__check_list__":[
              "screen_classification",
              "gather_information",
              "decision_making"
            ],
            "prompt_paths": {
              "inputs": {
                "screen_classification": "./res/prompts/gather_information/inputs/screen_classification.json",
                "gather_information": "./res/prompts/gather_information/inputs/gather_information.json",
                "decision_making": "./res/prompts/decision_making/inputs/decision_making.json"
              },
              "templates": {
                "screen_classification": "./res/prompts/gather_information/templates/screen_classification.prompt",
                "gather_information": "./res/prompts/gather_information/templates/gather_information.prompt",
                "decision_making": "./res/prompts/decision_making/templates/decision_making.prompt"
              }
            }
          }
        """

        super(BasePlanner, self).__init__()

        self.llm_provider = llm_provider

        self.use_screen_classification = use_screen_classification
        self.use_information_summary = use_information_summary
        self.gather_information_max_steps = gather_information_max_steps

        self.marker_matcher = marker_matcher
        self.object_detector = object_detector

        self.set_internal_params(planner_params, use_screen_classification, use_information_summary)

    # Allow re-configuring planner
    def set_internal_params(self, planner_params: Dict = None, use_screen_classification: bool = False, use_information_summary: bool = False):

        self.planner_params = planner_params

        if not check_planner_params(self.planner_params):
            raise ValueError(f"Error in planner_params: {self.planner_params}")

        self.inputs = self._init_inputs()
        self.templates = self._init_templates()

        if use_screen_classification:
            self.screen_classification_ = ScreenClassification(self.inputs["screen_classification"],
                                                               self.templates["screen_classification"],
                                                               self.llm_provider)
        else:
            self.screen_classification_ = None
            
        self.gather_information_ = GatherInformation(self.inputs["gather_information"],
                                                     self.templates["gather_information"],
                                                     self.marker_matcher,
                                                     self.object_detector,
                                                     self.llm_provider)
        
        self.decision_making_ = DecisionMaking(self.inputs["decision_making"],
                                               self.templates["decision_making"],
                                               self.llm_provider)
        
        self.success_detection_ = SuccessDetection(self.inputs["success_detection"],
                                                   self.templates["success_detection"],
                                                   self.llm_provider)

        if use_information_summary:
            self.information_summary_ = InformationSummary(self.inputs["information_summary"],
                                                    self.templates["information_summary"],
                                                    self.llm_provider)
        else:
            self.information_summary_ = None


    def _init_inputs(self):
        input_examples = dict()
        prompt_paths = self.planner_params["prompt_paths"]
        input_example_paths = prompt_paths["inputs"]
        for key, value in input_example_paths.items():
            path = assemble_project_path(value)
            if path.endswith(PROMPT_EXT):
                input_examples[key] = read_resource_file(path)
            else:
                input_examples[key] = load_json(path)
        return input_examples

    def _init_templates(self):
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
      
    def gather_information(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        if input is None:
            input = self.inputs["gather_information"]

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
            input = self.inputs["decision_making"]

        data = self.decision_making_(input=input)

        return data

    def success_detection(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        if input is None:
            input = self.inputs["success_detection"]

        data = self.success_detection_(input=input)

        return data

    def information_summary(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        if input is None:
            input = self.inputs["information_summary"]

        data = self.information_summary_(input=input)

        return data
