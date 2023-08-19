from abc import ABC, abstractmethod
from models import Tasks

class ExternalTask(ABC):

    @abstractmethod
    def UpdateEffort(self, task:Tasks):
        pass