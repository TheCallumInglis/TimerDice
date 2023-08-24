from abc import ABC, abstractmethod
from models import Tasks, Recording, ExternalTaskConfig

class ExternalTask(ABC):

    @abstractmethod
    def UpdateEffort(self, task:Tasks, recording:Recording):
        pass

    @abstractmethod
    def GetExternalTasks(self) -> list[ExternalTaskConfig]:
        pass

    @abstractmethod
    def GetExternalTaskByID(self, task_id) -> ExternalTaskConfig:
        pass

    @abstractmethod
    def SampleJsonConfig(self):
        pass