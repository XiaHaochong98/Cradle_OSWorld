import abc

from config.config import AbstractSingleton, Config

cfg = Config()


class MemoryProviderSingleton(AbstractSingleton):
    @abc.abstractmethod
    def put(self, data):
        pass

    @abc.abstractmethod
    def get(self, data):
        pass

    @abc.abstractmethod
    def clear(self):
        pass

    @abc.abstractmethod
    def get_relevant(self, data, max_relevant=3):
        pass

    @abc.abstractmethod
    def get_usage(self):
        pass
