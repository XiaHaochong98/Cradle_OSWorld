from copy import deepcopy

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

    # def to_text(self, template_str: str=None):
    #     template_str = deepcopy(template_str)

    #     template_str = template_str.replace('<system_content>', self.system_content)
    #     template_str = template_str.replace('<classes>', self.classes)
    #     template_str = template_str.replace('<few_shot_examples>', self.few_shot_examples)
    #     template_str = template_str.replace('<prompt>', self.prompt)

    #     return template_str


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
        self.system_content = get_attr(params, 'system_content', '')
        self.prompt = get_attr(params, 'prompt', '')
        self.__comments__ = get_attr(params, '__comments__', '')

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
        self.next_skill = get_attr(params, 'next_skill', '')
        self.skill_steps = get_attr(params, 'skill_steps', '')
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
        self.system_content = get_attr(params, 'system_content', '')
        self.prompt = get_attr(params, 'prompt', '')
        self.__comments__ = get_attr(params, '__comments__', '')

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
        self.decision = get_attr(params, 'decision', '')
        self.__comments__ = get_attr(params, '__comments__', '')

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

def json_encoder(object):
    if isinstance(object, ScreenClassificationInput):
        return {
            'type': object.type,
            'system_content': object.system_content,
            'classes': object.classes,
            'few_shot_examples': object.few_shot_examples,
            'prompt': object.prompt,
            '__comments__': object.__comments__
        }
    elif isinstance(object, GatherInformationInput):
        return {
            'type': object.type,
            'system_content': object.system_content,
            'prompt': object.prompt,
            'input': object.input,
            '__comments__': object.__comments__
        }
    elif isinstance(object, ScreenClassificationOutput):
        return {
            'type': object.type,
            'class': object.class_,
            '__comments__': object.__comments__
        }
    elif isinstance(object, GatherInformationOutput):
        return {
            'type': object.type,
            'objects': object.objects,
            'description': object.description,
            '__comments__': object.__comments__
        }
    elif isinstance(object, DecisionMakingInput):
        return {
            'type': object.type,
            'system_content': object.system_content,
            'prompt': object.prompt,
            '__comments__': object.__comments__
        }
    elif isinstance(object, DecisionMakingOutput):
        return {
            'type': object.type,
            'next_skill': object.next_skill,
            'skill_steps': object.skill_steps,
            '__comments__': object.__comments__
        }
    elif isinstance(object, SuccessDetectionInput):
        return {
            'type': object.type,
            'system_content': object.system_content,
            'prompt': object.prompt,
            '__comments__': object.__comments__
        }
    elif isinstance(object, SuccessDetectionOutput):
        return {
            'type': object.type,
            'success': object.success,
            '__comments__': object.__comments__
        }
    elif isinstance(object, Object):
        return {
            'type': object.type,
            'name': object.name,
            'bounding_box': object.bounding_box,
            'reasoning': object.reasoning,
            'value': object.value,
            'confidence': object.confidence
        }
    else:
        raise TypeError(f"Object of type {object.__class__.__name__} is not JSON serializable in json_encoder")

def json_decoder(object):
    if object['type'] == 'screen_classification':
        return ScreenClassificationInput(params=object)
    elif object['type'] == 'gather_information':
        return GatherInformationInput(params=object)
    elif object['type'] == 'screen_classification':
        return ScreenClassificationOutput(params=object)
    elif object['type'] == 'gather_information':
        return GatherInformationOutput(params=object)
    elif object['type'] == 'decision_making':
        return DecisionMakingInput(params=object)
    elif object['type'] == 'decision_making':
        return DecisionMakingOutput(params=object)
    elif object['type'] == 'success_detection':
        return SuccessDetectionInput(params=object)
    elif object['type'] == 'success_detection':
        return SuccessDetectionOutput(params=object)
    elif object['type'] == 'object':
        return Object(params=object)
    else:
        raise TypeError(f"Object of type {object['type']} is not JSON serializable in json_decoder")

__all__ = [
    'ScreenClassificationInput',
    'GatherInformationInput',
    'ScreenClassificationOutput',
    'GatherInformationOutput',
    'DecisionMakingInput',
    'DecisionMakingOutput',
    'SuccessDetectionInput',
    'SuccessDetectionOutput',
    'Object'
]