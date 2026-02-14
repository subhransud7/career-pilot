from abc import ABC, abstractmethod

class BaseAgent(ABC):

    @abstractmethod
    def execute(self, task_name: str, payload: dict) -> dict:
        pass
