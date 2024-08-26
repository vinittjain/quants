import yaml

from ..utils import get_logger
from .base import BaseConfig, BaseConfigLoader

logger = get_logger(__name__)


class BinanceConfigLoader(BaseConfigLoader):
    def __init__(self):
        pass

    def load_config(self, config_path: str) -> BaseConfig:
        try:
            with open(config_path, "r") as f:
                config_data = yaml.safe_load(f)
            logger.info(f"Configuration loaded successfully from {config_path}")
            return BaseConfig(**config_data)
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {str(e)}")
            raise

    def save_config(self, config: BaseConfig, config_path: str) -> None:
        try:
            config_dict = {
                "api_key": config.api_key,
                "api_secret": config.api_secret,
                "base_url": config.base_url,
                "platform": config.platform,
                "kline_intervals": config.kline_intervals,
                "data_path": config.data_path,
            }
            with open(config_path, "w") as f:
                yaml.dump(config_dict, f)
            logger.info(f"Configuration saved successfully to {config_path}")
        except Exception as e:
            logger.error(f"Error saving configuration to {config_path}: {str(e)}")
            raise
