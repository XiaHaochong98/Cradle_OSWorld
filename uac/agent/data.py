import json

from uac.config import Config
from uac.log import Logger
from uac.planner import BaseInput
from uac.planner import BaseOutput
from uac.planner.util import get_attr

config = Config()
logger = Logger()


class ScreenClassificationInput(BaseInput):
    def __init__(self, *args, params, **kwargs):
        super(ScreenClassificationInput, self).__init__(args = args, params=params, kwargs = kwargs)

        self.type = get_attr(params, 'type', 'screen_classification')
        self.system_content = get_attr(params, 'system_content', '')
        self.classes = get_attr(params, 'classes', [])
        self.few_shot_examples = get_attr(params, 'few_shot_examples', [])
        self.prompt = get_attr(params, 'prompt', '')
        self.__comments__ = get_attr(params, '__comments__', '')

        if not self.check():
            raise ValueError(f"Error in check ScreenClassificationInput: {params}")

    def check(self):
        flag = True
        try:
            assert self.type == 'screen_classification', f"type is not screen_classification"
        except Exception as e:
            logger.error(f"Error in check: {e}")
            flag = False

        return flag


class GatherInformationInput(BaseInput):
    def __init__(self, *args, params, **kwargs):
        super(GatherInformationInput, self).__init__(args = args, params=params, kwargs = kwargs)

        self.type = get_attr(params, 'type', 'gather_information')
        self.system_content = get_attr(params, 'system_content', '')
        self.prompt = get_attr(params, 'prompt', '')
        self.input = get_attr(params, 'input', '')
        self.__comments__ = get_attr(params, '__comments__', '')

        if not self.check():
            raise ValueError(f"Error in check GatherInformationInput: {params}")

    def check(self):
        flag = True
        try:
            assert self.type == 'gather_information', f"type is not gather_information"
        except Exception as e:
            logger.error(f"Error in check: {e}")
            flag = False

        return flag


class Object():
    def __init__(self, *args, params, **kwargs):
        self.type = get_attr(params, 'type', '')
        self.name = get_attr(params, 'name', '')
        self.bounding_box = get_attr(params, 'bounding_box', [])
        self.reasoning = get_attr(params, 'reasoning', '')
        self.value = get_attr(params, 'value', '')
        self.confidence = get_attr(params, 'confidence', '')
        self.__comments__ = get_attr(params, '__comments__', '')
        
        self.params = params

    def __eq__(self, other):
        return self.type == other.type and \
               self.name == other.name and \
               self.bounding_box == other.bounding_box and \
               self.reasoning == other.reasoning and \
               self.value == other.value and \
               self.confidence == other.confidence

    def __str__(self):
        return f"Object: {self.type}, {self.name}, {self.bounding_box}, {self.reasoning}, {self.value}, {self.confidence}"

    def __hash__(self):
        return hash(str(self))


class ScreenClassificationOutput(BaseOutput):
    def __init__(self, *args, params, **kwargs):
        super(ScreenClassificationOutput, self).__init__(args = args, params=params, kwargs = kwargs)

        self.type = get_attr(params, 'type', 'screen_classification')
        self.class_ = get_attr(params, 'class', '')
        self.__comments__ = get_attr(params, '__comments__', '')

        if not self.check():
            raise ValueError(f"Error in check ScreenClassificationOutput: {params}")

    def check(self):
        flag = True
        try:
            assert self.type == 'screen_classification', f"type is not screen_classification"
        except Exception as e:
            logger.error(f"Error in check: {e}")
            flag = False

        return flag


class GatherInformationOutput(BaseOutput):
    def __init__(self, *args, params, **kwargs):
        super(GatherInformationOutput, self).__init__(args = args, params=params, kwargs = kwargs)

        self.type = get_attr(params, 'type', 'gather_information')
        self.objects = get_attr(params, 'objects', '')
        self.objects = [Object(params=object_) for object_ in self.objects]
        self.description = get_attr(params, 'description', '')
        self.__comments__ = get_attr(params, '__comments__', '')

        if not self.check():
            raise ValueError(f"Error in check GatherInformationOutput: {params}")

    def check(self):
        flag = True
        try:
            assert self.type == 'gather_information', f"type is not gather_information"
        except Exception as e:
            logger.error(f"Error in check: {e}")
            flag = False

        return flag


class DecisionMakingInput(BaseInput):
    def __init__(self, *args, params, **kwargs):
        super(DecisionMakingInput, self).__init__(args = args, params=params, kwargs = kwargs)

        self.type = get_attr(params, 'type', 'decision_making')
        self.task_description = get_attr(params, 'task_description', '')
        self.skill_library = get_attr(params, 'skill_library', [])
        self.decision_making_memory_description = get_attr(params, 'decision_making_memory_description', '')
        self.gathered_information_description = get_attr(params, 'gathered_information_description', '')
        self.image_introduction = get_attr(params, 'image_introduction', [])
        self.output_format = get_attr(params, 'output_format', {})
        self.reasoning = get_attr(params, 'reasoning', '')
        self.__comments__ = get_attr(params, '__comments__', '')

        self.params = params

        if not self.check():
            raise ValueError(f"Error in check DecisionMakingInput: {params}")

    def check(self):
        flag = True
        try:
            assert self.type == 'decision_making', f"type is not decision_making"
        except Exception as e:
            logger.error(f"Error in check: {e}")
            flag = False

        return flag


class DecisionMakingOutput(BaseOutput):
    def __init__(self, *args, params, **kwargs):
        super(DecisionMakingOutput, self).__init__(args = args, params=params, kwargs = kwargs)

        self.type = get_attr(params, 'type', 'decision_making')
        self.skill_steps = get_attr(params, 'skill_steps', [])
        self.reasoning = get_attr(params, 'reasoning', '')
        self.__comments__ = get_attr(params, '__comments__', '')

        if not self.check():
            raise ValueError(f"Error in check DecisionMakingOutput: {params}")

    def check(self):
        flag = True
        try:
            assert self.type == 'decision_making', f"type is not decision_making"
        except Exception as e:
            logger.error(f"Error in check: {e}")
            flag = False

        return flag

class SuccessDetectionInput(BaseInput):
    def __init__(self, *args, params, **kwargs):
        super(SuccessDetectionInput, self).__init__(args = args, params=params, kwargs = kwargs)

        self.type = get_attr(params, 'type', 'success_detection')
        self.task_description = get_attr(params, 'task_descriptiont', '')
        self.image_instruction = get_attr(params, 'image_instruction', [])
        self.output_format = get_attr(params, 'output_format', {})
        self.__comments__ = get_attr(params, '__comments__', '')

        self.params = params

        if not self.check():
            raise ValueError(f"Error in check SuccessDetectionInput: {params}")

    def check(self):
        flag = True
        try:
            assert self.type == 'success_detection', f"type is not success_detection"
        except Exception as e:
            logger.error(f"Error in check: {e}")
            flag = False

        return flag


class SuccessDetectionOutput(BaseOutput):
    def __init__(self, *args, params, **kwargs):
        super(SuccessDetectionOutput, self).__init__(args = args, params=params, kwargs = kwargs)

        self.type = get_attr(params, 'type', 'success_detection')
        self.task_descriptio = get_attr(params, 'task_descriptio', '')
        self.decision = get_attr(params, 'decision', '')
        
        self.criteria = get_attr(self.decision, 'criteria', '')
        self.reasoning = get_attr(self.decision, 'reasoning', '')
        self.succcess = get_attr(self.decision, 'success', False)
        
        self.__comments__ = get_attr(params, '__comments__', '')
        
        self.params = params

        if not self.check():
            raise ValueError(f"Error in check SuccessDetectionOutput: {params}")

    def check(self):
        flag = True
        try:
            assert self.type == 'success_detection', f"type is not success_detection"
        except Exception as e:
            logger.error(f"Error in check: {e}")
            flag = False

        return flag



class InformationSummaryInput(BaseInput):
    def __init__(self, *args, params, **kwargs):
        super(InformationSummaryInput, self).__init__(args = args, params=params, kwargs = kwargs)

        self.type = get_attr(params, 'type', 'information_summary')
        self.history_information = get_attr(params, 'history_information', '')
        self.output_format = get_attr(params, 'output_format', {})
        self.__comments__ = get_attr(params, '__comments__', '')

        self.params = params

        if not self.check():
            raise ValueError(f"Error in check InformationSummaryInput: {params}")

    def check(self):
        flag = True
        try:
            assert self.type == 'information_summary', f"type is not information_summary"
        except Exception as e:
            logger.error(f"Error in check: {e}")
            flag = False

        return flag


class InformationSummaryOutput(BaseOutput):
    def __init__(self, *args, params, **kwargs):
        super(InformationSummaryOutput, self).__init__(args = args, params=params, kwargs = kwargs)

        self.type = get_attr(params, 'type', 'information_summary')
        self.info_summary = get_attr(params, 'info_summary', '')
        
        self.__comments__ = get_attr(params, '__comments__', '')
        
        self.params = params

        if not self.check():
            raise ValueError(f"Error in check InformationSummaryOutput: {params}")

    def check(self):
        flag = True
        try:
            assert self.type == 'information_summary', f"type is not information_summary"
        except Exception as e:
            logger.error(f"Error in check: {e}")
            flag = False

        return flag
    
def json_encoder(object):
    return object.params

def json_decoder(params):
    if params['type'] == 'screen_classification':
        return ScreenClassificationInput(params=params)
    elif params['type'] == 'gather_information':
        return GatherInformationInput(params=params)
    elif params['type'] == 'screen_classification':
        return ScreenClassificationOutput(params=params)
    elif params['type'] == 'gather_information':
        return GatherInformationOutput(params=params)
    elif params['type'] == 'decision_making':
        return DecisionMakingInput(params=params)
    elif params['type'] == 'decision_making':
        return DecisionMakingOutput(params=params)
    elif params['type'] == 'success_detection':
        return SuccessDetectionInput(params=params)
    elif params['type'] == 'success_detection':
        return SuccessDetectionOutput(params=params)
    elif params['type'] == 'information_summary':
        return InformationSummaryInput(params=params)
    elif params['type'] == 'information_summary':
        return InformationSummaryOutput(params=params)
    elif params['type'] == 'params':
        return params(params=params)
    else:
        raise TypeError(f"params of type {params['type']} is not JSON serializable in json_decoder")
