import abc

from uac.config import Config
from uac.log import Logger

cfg = Config()
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

    @abc.abstractmethod
    def loop(self, *args, **kwargs):
        """
        loop for the task
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