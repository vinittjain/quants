import yaml
from typing import List, Dict, Any
from dataclasses import dataclass

class ConfigLoader:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config_data = self._load_yaml()

    def _load_yaml(self) -> Dict[str, Any]:
        with open(self.config_path, 'r') as file:
            return yaml.safe_load(file)

    def get_cex_config(self) -> Dict[str, Any]:
        return self.config_data.get('cex', {})

    def get_strategies_config(self) -> Dict[str, Any]:
        return self.config_data.get('strategies', {})

    def get_full_config(self) -> Dict[str, Any]:
        return self.config_data

    def save_config(self, config: Dict[str, Any]):
        with open(self.config_path, 'w') as file:
            yaml.dump(config, file)


@dataclass
class CEXConfig:
    api_key: str
    api_secret: str
    base_url: str
    platform: str
    kline_intervals: List[str]
    data_path: str
    timezone: str

@dataclass
class StrategyConfig:
    name: str
    parameters: Dict[str, Any]

@dataclass
class AppConfig:
    cex: CEXConfig
    strategies: Dict[str, StrategyConfig]