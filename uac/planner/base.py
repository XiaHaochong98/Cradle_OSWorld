import abc
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)
import json

from uac.config import Config
from uac.log import Logger

config = Config()
logger = Logger()


class BasePlanner():
    def __init__(self,
                 ):
        pass

    @abc.abstractmethod
    def gather_information(self, *args, **kwargs) -> Dict[str, Any]:
        """
        gather information for the task
        :param args:
        :param kwargs:
        :return:
        """
        pass

    @abc.abstractmethod
    def decision_making(self, *args, **kwargs) -> Dict[str, Any]:
        """
        generate the next skill
        :param args:
        :param kwargs:
        :return:
        """
        pass

    @abc.abstractmethod
    def success_detection(self, *args, **kwargs) -> Dict[str, Any]:
        """
        detect whether the task is success
        :param args:
        :param kwargs:
        :return:
        """
        pass


class BaseInput():
    def __init__(self, *args, params: Dict[str, Any], **kwargs):
        self.params = params
        pass

    @abc.abstractmethod
    def _check(self):
        pass

    def to_text(self, template_str: str = None, params: Dict[str, Any] = None) -> str:
        if params is None:
            params = self.params

        return to_text(template_str, params)


def to_text(template_str: str = None, params: Dict[str, Any] = None) -> str:

    str = template_str

    if template_str is None or params is None:
        return str

    if type(params) is tuple:
        params = params[0]

    keys = params.keys()
    for key in keys:
        if key in template_str:
            if isinstance(params[key], list) or isinstance(params[key], dict):
                str = str.replace(f'<${key}$>', json.dumps(params[key], indent=4))
            else:

                if params[key] is None:

                    logger.warn(f"Value for: {key} is None!")
                    params[key] = ''
                    
                str = str.replace(f'<${key}$>', params[key])
    return str


class BaseOutput():
    def __init__(self, *args, params: Dict[str, Any], **kwargs):
        self.params = params
        pass

    @abc.abstractmethod
    def _check(self):
        pass


class BaseTemplate():
    def __init__(self, *args, params, **kwargs):
        self.params = params
        pass

    @abc.abstractmethod
    def _check(self):
        pass