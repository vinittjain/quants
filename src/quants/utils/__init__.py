from typing import Any, Dict, Type

from .logger import setup_logging


class Singleton(type):
    """Singleton metaclass for ensuring only one instance of a class"""

    _instances: Dict[Type[Any], Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


__all__ = ["setup_logging", "Singleton"]
