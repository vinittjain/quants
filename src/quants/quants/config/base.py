from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class BaseConfig:
    api_key: str
    api_secret: str
    base_url: str
    platform: str
    kline_intervals: List[str]
    data_path: str


class BaseConfigLoader(ABC):
    @abstractmethod
    def load_config(self, config_path: str) -> BaseConfig:
        pass

    @abstractmethod
    def save_config(self, config: BaseConfig, config_path: str) -> None:
        pass
