import abc

from uac.config import Config
from uac.log import Logger

config = Config()
logger = Logger()

class BasePlanner():
    def __init__(self,
                 ):
        pass

    @abc.abstractmethod
    def gather_information(self, *args, **kwargs):
        """
        gather information for the task
        :param args:
        :param kwargs:
        :return:
        """
        pass

    @abc.abstractmethod
    def decision_making(self, *args, **kwargs):
        """
        generate the next skill
        :param args:
        :param kwargs:
        :return:
        """
        pass

    @abc.abstractmethod
    def success_detection(self, *args, **kwargs):
        """
        detect whether the task is success
        :param args:
        :param kwargs:
        :return:
        """
        pass


class BaseInput():
    def __init__(self, *args, params, **kwargs):
        self.params = params
        pass

    @abc.abstractmethod
    def _check(self):
        pass

    def to_text(self, template_str: str = None, params: dict = None) -> str:

        str = template_str

        if template_str is None or params is None:
            return str

        if type(params) is tuple:
            params = params[0]

        keys = params.keys()
        for key in keys:
            if key in template_str:            
                str = str.replace(f'<${key}$>', params[key])

        return str


class BaseOutput():
    def __init__(self, *args, params, **kwargs):
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