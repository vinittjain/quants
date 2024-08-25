from abc import ABC, abstractmethod
from typing import Any, Callable, Dict


class BaseTaskScheduler(ABC):
    @abstractmethod
    def add_task(self, name: str, interval: str, task: Callable, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def remove_task(self, name: str) -> None:
        pass

    @abstractmethod
    def get_tasks(self) -> Dict[str, Dict[str, Any]]:
        pass

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
