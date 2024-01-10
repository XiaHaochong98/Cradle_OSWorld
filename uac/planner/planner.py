import json
from typing import Dict, Any, List
import os

from uac.config import Config
from uac.log import Logger
from uac.planner.base import BasePlanner
from uac.provider.base_llm import LLMProvider
from uac.provider import GdProvider
from uac.utils.check import check_planner_params
from uac.utils.json_utils import load_json, parse_semi_formatted_json, parse_semi_formatted_text
from uac.utils.file_utils import assemble_project_path, read_resource_file
from uac.gameio.video.VideoFrameExtractor import JSONStructure
import aiohttp
import asyncio

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

    def _pre(self, *args, input=None, screenshot_file=None, **kwargs):
        return input, screenshot_file

    def __call__(self, *args, input=None, screenshot_file=None, **kwargs):
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

    def _post(self, *args, data=None, **kwargs):
        return data


class GatherInformation():

    def __init__(self,
                 input_map: Dict = None,
                 template: str = None,
                 marker_matcher: Any = None,
                 object_detector: Any = None,
                 llm_provider: LLMProvider = None,
                 get_text_input_map: Dict = None,
                 get_text_template: str = None,
                 frame_extractor: Any = None
                 ):

        self.input_map = input_map
        self.template = template
        self.marker_matcher = marker_matcher
        self.object_detector = object_detector
        self.llm_provider = llm_provider
        self.get_text_input_map = get_text_input_map
        self.get_text_template = get_text_template
        self.frame_extractor = frame_extractor

    def _pre(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return input

    def __call__(self, *args, input: Dict[str, Any] = None, class_=None, **kwargs) -> Dict[str, Any]:
        async def gather_information_get_completion_parallel(current_frame_path,time_stamp,get_text_input,i):
            logger.write(f"Start gathering text information from the {i + 1}/{len(extracted_frame_paths)} frame")
            get_text_input = self.get_text_input_map if get_text_input is None else get_text_input

            image_introduction = [
                {
                    "introduction": get_text_input["image_introduction"][-1]["introduction"],
                    "path": f"{current_frame_path}",
                    "assistant": get_text_input["image_introduction"][-1]["assistant"]
                }
            ]
            get_text_input["image_introduction"] = image_introduction

            message_prompts = self.llm_provider.assemble_prompt(template_str=self.get_text_template,
                                                                params=get_text_input)

            logger.debug(f'>> Upstream - R: {message_prompts}')

            response, info = await self.llm_provider.create_completion_async(message_prompts)

            logger.debug(f'>> Downstream - A: {response}')
            success_flag = False
            while not success_flag:
                try:
                    # Convert the response to dict
                    processed_response = parse_semi_formatted_text(response)
                    success_flag = True
                except Exception as e:
                    logger.error(f"Response is not in the correct format: {e}, retrying...")
                    success_flag = False
            # Convert the response to dict
            if processed_response is None or len(response) == 0:
                logger.warn('Empty response in gather text information call')
                logger.debug("response",response,"processed_response",processed_response)
            objects = processed_response
            objects_index = str(video_prefix) + '_' + time_stamp
            gathered_information_JSON.add_instance(objects_index, objects)
            logger.write(f"Finish gathering text information from the {i + 1}/{len(extracted_frame_paths)} frame")

            return True

        def gather_information_get_completion_sequence(current_frame_path,time_stamp,get_text_input,i):
            logger.write(f"Start gathering text information from the {i + 1}/{len(extracted_frame_paths)} frame")
            get_text_input = self.get_text_input_map if get_text_input is None else get_text_input

            image_introduction = [
                {
                    "introduction": get_text_input["image_introduction"][-1]["introduction"],
                    "path": f"{current_frame_path}",
                    "assistant": get_text_input["image_introduction"][-1]["assistant"]
                }
            ]
            get_text_input["image_introduction"] = image_introduction

            message_prompts = self.llm_provider.assemble_prompt(template_str=self.get_text_template,
                                                                params=get_text_input)

            logger.debug(f'>> Upstream - R: {message_prompts}')

            response, info = self.llm_provider.create_completion(message_prompts)

            logger.debug(f'>> Downstream - A: {response}')
            success_flag = False
            while not success_flag:
                try:
                    # Convert the response to dict
                    processed_response = parse_semi_formatted_text(response)
                    success_flag = True
                except Exception as e:
                    logger.error(f"Response is not in the correct format: {e}, retrying...")
                    success_flag = False
                # Convert the response to dict
            if processed_response is None or len(response) == 0:
                logger.warn('Empty response in gather text information call')
                logger.debug("response",response,"processed_response",processed_response)
            objects = processed_response
            objects_index = str(video_prefix) + '_' + time_stamp
            gathered_information_JSON.add_instance(objects_index, objects)
            logger.write(f"Finish gathering text information from the {i + 1}/{len(extracted_frame_paths)} frame")

            return True

        async def get_completion_in_parallel(extracted_frame_paths,get_text_input):
            tasks = [gather_information_get_completion_parallel(current_frame_path, time_stamp,get_text_input,i) for i, (current_frame_path, time_stamp) in enumerate(extracted_frame_paths)]
            return await asyncio.gather(*tasks)

        def get_completion_in_sequence(extracted_frame_paths,get_text_input):
            for i, (current_frame_path, time_stamp) in enumerate(extracted_frame_paths):
                gather_information_get_completion_sequence(current_frame_path, time_stamp, get_text_input, i)
            return True


        flag = True
        if self.frame_extractor is not None:
            get_text_input=input["get_text_input"]
            video_path = input["video_clip_path"]
            # extract the text information of the whole video
            # run the frame_extractor to get the key frames
            extracted_frame_paths=self.frame_extractor.extract(video_path=video_path)
            # for each key frame, use llm to get the text information
            video_prefix = os.path.basename(video_path).split('.')[0].split('_')[-1] # different video should have differen prefix for avoiding the same time stamp
            gathered_information_JSON = JSONStructure()
            if config.parallel_request_gather_information:
                # create completion in parallel
                logger.write(f"Start gathering text information from the whole video in parallel")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(get_completion_in_parallel(extracted_frame_paths, get_text_input))
                except KeyboardInterrupt:
                    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
                    for task in tasks:
                        task.cancel()
                    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
                finally:
                    loop.close()
            else:
                logger.write(f"Start gathering text information from the whole video in sequence")
                get_completion_in_sequence(extracted_frame_paths, get_text_input)
            gathered_information_JSON.sort_index_by_timestamp()
            logger.write(f"Finish gathering text information from the whole video")

        else:
            gathered_information_JSON=None

        input = self.input_map if input is None else input
        input = self._pre(input=input)

        image_files = []
        if "image_introduction" in input.keys():
            for image_info in input["image_introduction"]:
                image_files.append(image_info["path"])

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

        # Gather information by LLM provider - mandatory
        try:
            # Call the LLM provider for gather information json
            message_prompts = self.llm_provider.assemble_prompt(template_str=self.template, params=input)

            logger.debug(f'>> Upstream - R: {message_prompts}')
            response, info = self.llm_provider.create_completion(message_prompts)

            logger.debug(f'>> Downstream - A: {response}')
            # Convert the response to dict
            processed_response = parse_semi_formatted_text(response)

            llm_provider_gather_information = processed_response

        except Exception as e:
            logger.error(f"Error in gather image description information: {e}")
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

            # merge the gathered_information_JSON to the processed_response
            processed_response["gathered_information_JSON"]=gathered_information_JSON

            res_dict = processed_response

            # res_json = json.dumps(processed_response, indent=4)
            
        # Gather information by object detector, which is grounding dino.
        if self.object_detector is not None:
            try:
                image_source, boxes, logits, phrases = self.object_detector.detect(image_path=image_files[0], text_prompt=processed_response["target_object_name"].title(), box_threshold=0.4, device='cuda')
                processed_response["boxes"] = boxes
                processed_response["logits"] = logits
                processed_response["phrases"] = phrases
                # directory, filename = os.path.split(image_files[0])
                # bb_image_path = os.path.join(directory, "bb_"+filename)
                # self.object_detector.save_annotate_frame(image_source, boxes, logits, phrases, res_dict["target_object_name"].title(), bb_image_path)
            except Exception as e:
                logger.error(f"Error in gather information by object detector: {e}")
                flag = False

        success = self._check_success(data=processed_response)

        data = dict(
            flag=flag,
            success=success,
            input=input,
            res_dict=processed_response,
            # res_json = res_json
        )

        data = self._post(data=data)

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
        processed_response = {}

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
            # processed_response = parse_semi_formatted_json(response)

            processed_response = parse_semi_formatted_text(response)

            # res_json = json.dumps(processed_response, indent=4)

        except Exception as e:
            logger.error(f"Error in decision_making: {e}")
            logger.error_ex(e)
            flag = False

        data = dict(
            flag=flag,
            input=input,
            res_dict=processed_response,
            # res_json = res_json,
        )

        data = self._post(data=data)
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
        # res_json = None

        try:

            # Call the LLM provider for success detection
            message_prompts = self.llm_provider.assemble_prompt(template_str=self.template, params=input)

            logger.debug(f'>> Upstream - R: {message_prompts}')

            response, info = self.llm_provider.create_completion(message_prompts)

            logger.debug(f'>> Downstream - A: {response}')

            # Convert the response to dict
            # processed_response = parse_semi_formatted_json(response)

            processed_response = parse_semi_formatted_text(response)

            # res_json = json.dumps(processed_response, indent=4)

        except Exception as e:
            logger.error(f"Error in success_detection: {e}")
            flag = False

        data = dict(
            flag=flag,
            input=input,
            # res_json=res_json,
            res_dict=processed_response,
        )

        data = self._post(data=data)
        return data

    def _post(self, *args, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        return data


class SelfReflection():
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
        # res_json = None

        try:

            # Call the LLM provider for self reflection
            message_prompts = self.llm_provider.assemble_prompt(template_str=self.template, params=input)

            logger.debug(f'>> Upstream - R: {message_prompts}')

            response, info = self.llm_provider.create_completion(message_prompts)

            logger.debug(f'>> Downstream - A: {response}')

            # Convert the response to dict
            # processed_response = parse_semi_formatted_json(response)

            processed_response = parse_semi_formatted_text(response)

            # res_json = json.dumps(processed_response, indent=4)

        except Exception as e:
            logger.error(f"Error in self reflection: {e}")
            flag = False

        data = dict(
            flag=flag,
            input=input,
            # res_json=res_json,
            res_dict=processed_response,
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
        res_json = None

        try:

            # Call the LLM provider for information summary
            message_prompts = self.llm_provider.assemble_prompt(template_str=self.template, params=input)

            logger.debug(f'>> Upstream - R: {message_prompts}')

            response, info = self.llm_provider.create_completion(message_prompts)

            logger.debug(f'>> Downstream - A: {response}')

            # Convert the response to dict
            # processed_response = parse_semi_formatted_json(response)

            processed_response = parse_semi_formatted_text(response)

            # res_json = json.dumps(processed_response, indent=4)

        except Exception as e:
            logger.error(f"Error in information_summary: {e}")
            flag = False

        data = dict(
            flag=flag,
            input=input,
            res_dict=processed_response,
            # res_json=res_json,
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
                 use_self_reflection: bool = False,
                 gather_information_max_steps: int = 1,  # 5,
                 marker_matcher: Any = None,
                 object_detector: Any = None,
                 frame_extractor: Any = None,
                 ):
        """
        inputs: input key-value pairs
        templates: template for composing the prompt

        planner_params = {
            "__check_list__":[
              "screen_classification",
              "gather_information",
              "decision_making",
              "information_summary",
              "self_reflection"
            ],
            "prompt_paths": {
              "inputs": {
                "screen_classification": "./res/prompts/inputs/screen_classification.json",
                "gather_information": "./res/prompts/inputs/gather_information.json",
                "decision_making": "./res/prompts/inputs/decision_making.json",
                "success_detection": "./res/prompts/inputs/success_detection.json",
                "information_summary": "./res/prompts/inputs/information_summary.json",
                "self_reflection": "./res/prompts/inputs/self_reflection.json",
              },
              "templates": {
                "screen_classification": "./res/prompts/templates/screen_classification.prompt",
                "gather_information": "./res/prompts/templates/gather_information.prompt",
                "decision_making": "./res/prompts/templates/decision_making.prompt",
                "success_detection": "./res/prompts/templates/success_detection.prompt",
                "information_summary": "./res/prompts/templates/information_summary.prompt",
                "self_reflection": "./res/prompts/templates/self_reflection.prompt",
              }
            }
          }
        """

        super(BasePlanner, self).__init__()

        self.llm_provider = llm_provider

        self.use_screen_classification = use_screen_classification
        self.use_information_summary = use_information_summary
        self.use_self_reflection = use_self_reflection
        self.gather_information_max_steps = gather_information_max_steps

        self.marker_matcher = marker_matcher
        self.object_detector = object_detector
        self.frame_extractor = frame_extractor
        self.set_internal_params(planner_params=planner_params,
                                 use_screen_classification=use_screen_classification,
                                 use_information_summary=use_information_summary)

    # Allow re-configuring planner
    def set_internal_params(self,
                            planner_params: Dict = None,
                            use_screen_classification: bool = False,
                            use_information_summary: bool = False):

        self.planner_params = planner_params
        if not check_planner_params(self.planner_params):
            raise ValueError(f"Error in planner_params: {self.planner_params}")

        self.inputs = self._init_inputs()
        self.templates = self._init_templates()

        if use_screen_classification:
            self.screen_classification_ = ScreenClassification(input_example=self.inputs["screen_classification"],
                                                               template=self.templates["screen_classification"],
                                                               llm_provider=self.llm_provider)
        else:
            self.screen_classification_ = None

        self.gather_information_ = GatherInformation(input_map=self.inputs["gather_information"],
                                                     template=self.templates["gather_information"],
                                                     get_text_input_map=self.inputs["gather_text_information"],
                                                     get_text_template=self.templates["gather_text_information"],
                                                     frame_extractor=self.frame_extractor,
                                                     marker_matcher=self.marker_matcher,
                                                     object_detector=self.object_detector,
                                                     llm_provider=self.llm_provider)

        self.decision_making_ = DecisionMaking(input_map=self.inputs["decision_making"],
                                               template=self.templates["decision_making"],
                                               llm_provider=self.llm_provider)

        self.success_detection_ = SuccessDetection(input_map=self.inputs["success_detection"],
                                                   template=self.templates["success_detection"],
                                                   llm_provider=self.llm_provider)

        if self.use_self_reflection:
            self.self_reflection_ = SelfReflection(input_map=self.inputs["self_reflection"],
                                                   template=self.templates["self_reflection"],
                                                   llm_provider=self.llm_provider)
        else:
            self.self_reflection_ = None

        if use_information_summary:
            self.information_summary_ = InformationSummary(input_map=self.inputs["information_summary"],
                                                           template=self.templates["information_summary"],
                                                           llm_provider=self.llm_provider)
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

    def self_reflection(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        if input is None:
            input = self.inputs["self_reflection"]

        data = self.self_reflection_(input=input)

        return data

    def information_summary(self, *args, input: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:

        if input is None:
            input = self.inputs["information_summary"]

        data = self.information_summary_(input=input)

        return data