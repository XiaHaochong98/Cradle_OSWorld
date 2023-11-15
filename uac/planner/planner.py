import json
import os
from typing import Dict, Any
from copy import deepcopy

from uac.config import Config
from uac.log import Logger
from uac.planner.base import BasePlanner
from uac.planner.helper import (ScreenClassificationInput,
                                GatherInformationInput,
                                GatherInformationOutput,
                                ScreenClassificationOutput,
                                json_encoder,
                                json_decoder)
from uac.utils.check import check_planner_params
from uac.utils.json_utils import load_json

cfg = Config()
logger = Logger()

class ScreenClassification():
    def __init__(self,
                 *args,
                 input_example: Dict = None,
                 template: Dict = None,
                 output_example: Dict = None,
                 llm_provider: Any = None,
                 **kwargs,):

        self.input_example = input_example
        self.template = template
        self.output_example = output_example
        self.llm_provider = llm_provider

    def _pre(self, *args, input = None, screen_shoot = None, **kwargs):
        return input, screen_shoot

    def __call__(self, *args, input = None, screen_shoot = None, **kwargs):

        input = self.input_example if input is None else input
        input = self._pre(input=input, screen_shoot=screen_shoot)

        # get the current screen classification
        flag = True
        class_ = None
        try:
            image = deepcopy(screen_shoot)
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
            screen_shoot = screen_shoot,
            class_= class_,
        )
        data = self._post(data = data)
        return data

    def _post(self, *args, data = None, **kwargs):
        return data

class GatherInformation():

    def __init__(self,
                    *args,
                    input_example: Dict = None,
                    template: Dict = None,
                    output_example: Dict = None,
                    marker_matcher: Any = None,
                    object_detector: Any = None,
                    llm_provider: Any = None,):

        self.input_example = input_example
        self.template = template
        self.output_example = output_example
        self.marker_matcher = marker_matcher
        self.object_detector = object_detector
        self.llm_provider = llm_provider

    def _pre(self, *args, input = None, screen_shoot = None, **kwargs):
        return input, screen_shoot

    def __call__(self, *args, input = None, screen_shoot = None, class_ = None, **kwargs):
        input = self.input_example if input is None else input
        input = self._pre(input=input, screen_shoot=screen_shoot)

        flag = True
        res_json = None

        marker_matcher_gathered_information_output = None
        object_detector_gathered_information_output = None
        llm_provider_gather_information_output = None

        # gather information by marker matcher
        try:
            marker_matcher_gathered_information = self.marker_matcher(screen_shoot=screen_shoot, class_=class_)
            marker_matcher_gathered_information_output = GatherInformationOutput(params=marker_matcher_gathered_information)
        except Exception as e:
            logger.error(f"Error in gather information by marker matcher: {e}")
            flag = False

        # gather information by object detector
        try:
            object_detector_gathered_information = self.object_detector(screen_shoot=screen_shoot, class_=class_)
            object_detector_gathered_information_output = GatherInformationOutput(params=object_detector_gathered_information)
        except Exception as e:
            logger.error(f"Error in gather information by object detector: {e}")
            flag = False

        # gather information by LLM provider
        try:
            image = deepcopy(screen_shoot)
            gather_information_input = GatherInformationInput(params=input)
            content = gather_information_input.to_text(template_str=self.template["template"])

            # call the LLM provider for gather information json
            response_json = self.llm_provider(content=content, image=image).json()

            # convert the json to dict
            response_dict = json.loads(response_json)

            # convert the dict to GatherInformationOutput
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
            screen_shoot = screen_shoot,
            res_json = res_json
        )

        data = self._post(data = data)

        return data


    def _post(self, *args, data = None, **kwargs):
        return data

    def _check_success(self, *args, res_json, **kwargs):
        success = False
        return success


class DecisionMaking():
    def __init__(self,
                 *args,
                 input_example: Dict = None,
                 template: Dict = None,
                 output_example: Dict = None,
                 llm_provider: Any = None,
                 memory: Any = None,
                 **kwargs,):

        self.input_example = input_example
        self.template = template
        self.output_example = output_example
        self.llm_provider = llm_provider
        self.memory = memory

    def _pre(self, *args, input = None, screen_shoot = None, **kwargs):
        return input, screen_shoot

    def __call__(self, *args, input = None, screen_shoot = None, **kwargs):

        input = self.input_example if input is None else input
        input = self._pre(input=input, screen_shoot=screen_shoot)

        flag = True
        try:
            image = deepcopy(screen_shoot)

            decision_making_description = self.memory.get("decision_making_description")
            input["decision_making_description"] = decision_making_description

            decision_making_input = DecisionMakingInput(params=input)
            content = decision_making_input.to_text(template_str=self.template["template"])

            # call the LLM provider for screen classification json
            response_json = self.llm_provider(content=content, image=image).json()

            # convert the json to dict
            response_dict = json.loads(response_json)

            # convert the dict to ScreenClassificationOutput
            decision_making_output = DecisionMakingOutput(params=response_dict)

        except Exception as e:
            logger.error(f"Error in gather_information: {e}")
            flag = False

        res_json = json.dumps(decision_making_output, default=json_encoder, indent=4)

        data = dict(
            flag = flag,
            input = input,
            screen_shoot = screen_shoot,
            res_json = res_json
        )
        data = self._post(data = data)
        return data

    def _post(self, *args, data = None, **kwargs):
        return data


class SuccessDetection():
    def __init__(self,
                 *args,
                 input_example: Dict = None,
                 template: Dict = None,
                 output_example: Dict = None,
                 llm_provider: Any = None,
                 memory: Any = None,
                 **kwargs,):

        self.input_example = input_example
        self.template = template
        self.output_example = output_example
        self.llm_provider = llm_provider
        self.memory = memory

    def _pre(self, *args, input = None, screen_shoot = None, **kwargs):
        return input, screen_shoot

    def __call__(self, *args, input = None, screen_shoot = None, **kwargs):

        input = self.input_example if input is None else input
        input = self._pre(input=input, screen_shoot=screen_shoot)

        flag = True
        success = None
        try:
            image = deepcopy(screen_shoot)

            success_detection_description = self.memory.get("success_detection_description")
            input["success_detection_description"] = success_detection_description

            success_detection_input = SuccessDetectionInput(params=input)
            content = success_detection_input.to_text(template_str=self.template["template"])

            # call the LLM provider for screen classification json
            response_json = self.llm_provider(content=content, image=image).json()

            # convert the json to dict
            response_dict = json.loads(response_json)

            # convert the dict to ScreenClassificationOutput
            success_detection_output = SuccessDetectionOutput(params=response_dict)

            success = success_detection_output.success

        except Exception as e:
            logger.error(f"Error in gather_information: {e}")
            flag = False

        data = dict(
            flag = flag,
            input = input,
            screen_shoot = screen_shoot,
            success = success
        )
        data = self._post(data = data)
        return data

    def _post(self, *args, data = None, **kwargs):
        return data

class Planner(BasePlanner):
    def __init__(self,
                 *args,
                 planner_params: Dict = None,
                 use_screen_classification: bool = True,
                 gather_information_max_steps: int = 5,
                 llm_provider: Any = None,
                 marker_matcher: Any = None,
                 object_detector: Any = None,
                 memory: Any = None,
                 game: Any = None,
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
                "screen_classification": "res/prompts/gather_information/input_example/screen_classification.json",
                "gather_information": "res/prompts/gather_information/input_example/gather_information.json",
                "decision_making": "res/prompts/decision_making/input_example/decision_making.json"
              },
              "template": {
                "screen_classification": "res/prompts/gather_information/template/screen_classification.json",
                "gather_information": "res/prompts/gather_information/template/gather_information.json",
                "decision_making": "res/prompts/decision_making/template/decision_making.json"
              },
              "output_example": {
                "screen_classification": "res/prompts/gather_information/output_example/screen_classification.json",
                "gather_information": "res/prompts/gather_information/output_example/gather_information.json",
                "decision_making": "res/prompts/decision_making/output_example/decision_making.json"
              }
            }
          }
        """

        super(BasePlanner, self).__init__()
        self.planner_params = planner_params
        self.use_screen_classification = use_screen_classification
        self.gather_information_max_steps = gather_information_max_steps

        self.llm_provider = llm_provider
        self.marker_matcher = marker_matcher
        self.object_detector = object_detector

        self.memory = memory
        self.game = game

        if not check_planner_params(self.planner_params):
            raise ValueError(f"Error in planner_params: {self.planner_params}")

        self.input_examples = self._init_input_example()
        self.templates = self._init_template()
        self.output_examples = self._init_output_example()

        self.screen_classification = ScreenClassification(self.input_examples["screen_classification"],
                                                          self.templates["screen_classification"],
                                                          self.output_examples["screen_classification"])
        self.gather_information = GatherInformation(self.input_examples["gather_information"],
                                                    self.templates["gather_information"],
                                                    self.output_examples["gather_information"],
                                                    self.marker_matcher,
                                                    self.object_detector,
                                                    self.llm_provider)
        self.decision_making = DecisionMaking(self.input_examples["decision_making"],
                                                self.templates["decision_making"],
                                                self.output_examples["decision_making"],
                                                self.llm_provider,
                                                self.memory)

    def _init_input_example(self):
        input_examples = dict()
        prompt_paths = self.planner_params["prompt_paths"]
        input_example_paths = prompt_paths["input_example"]
        for key, value in input_example_paths.items():
            path = os.path.join(cfg.work_dir, value)
            input_examples[key] = load_json(path)
        return input_examples

    def _init_template(self):
        templates = dict()
        prompt_paths = self.planner_params["prompt_paths"]
        template_paths = prompt_paths["template"]
        for key, value in template_paths.items():
            path = os.path.join(cfg.work_dir, value)
            templates[key] = load_json(path)
        return templates

    def _init_output_example(self):
        output_examples = dict()
        prompt_paths = self.planner_params["prompt_paths"]
        output_example_paths = prompt_paths["output_example"]
        for key, value in output_example_paths.items():
            path = os.path.join(cfg.work_dir, value)
            output_examples[key] = load_json(path)
        return output_examples

    def gather_information(self, *args, screen_shoot, **kwargs):

        input = self.input_examples["gather_information"]
        if self.use_screen_classification:
            class_ = self.screen_classification(screen_shoot=screen_shoot)["class_"]
        else:
            class_ = None

        for i in range(self.gather_information_max_steps):
            data = self.gather_information(input=input, screen_shoot=screen_shoot, class_=class_)

            success = data["success"]

            if success:
                break

            # next input and screen_shoot
            input = data["input"]
            screen_shoot = data["screen_shoot"]

        res_json = data["res_json"]

        self.memory.update(res_json)

    def decision_making(self, *args, screen_shoot, **kwargs):
        data = self.decision_making(screen_shoot=screen_shoot)
        res_json = data["res_json"]
        self.memory.update(res_json)
        self.game.execute(res_json)

    def success_detection(self, *args, **kwargs):
        data = self.success_detection()
        success = data["success"]
        return success

    def loop(self, *args, screen_shot, **kwargs):
        success = False

        while not success:
            self.gather_information(screen_shoot=screen_shot)
            self.decision_making(screen_shoot=screen_shot)
            success = self.success_detection()
            screen_shot = self.game.screen_shot()