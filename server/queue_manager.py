from abc import ABC, abstractmethod


class QueueManager(ABC):

    @abstractmethod
    def put(self, *args):
        pass

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def name(self):
        pass
