from .base import CEXConfig, StrategyConfig, AppConfig, DataStorageConfig, AnalysisConfig, ConfigLoader
from typing import Dict, Any

class ConfigFactory:
    @staticmethod
    def create_cex_config(config_data: Dict[str, Any]) -> CEXConfig:
        return CEXConfig(**config_data)
    
    @staticmethod
    def create_analysis_config(config_data: Dict[str, Any]) -> AnalysisConfig:
        return AnalysisConfig(**config_data)

    @staticmethod
    def create_strategy_config(name: str, config_data: Dict[str, Any]) -> StrategyConfig:
        return StrategyConfig(**config_data)

    @staticmethod   
    def create_data_storage_config(config_data: Dict[str, Any]) -> DataStorageConfig:
        return DataStorageConfig(**config_data)

    @staticmethod
    def create_app_config(config_data: Dict[str, Any]) -> AppConfig:
        cex_config = ConfigFactory.create_cex_config(config_data.get_cex_config())
        data_storage_config = ConfigFactory.create_data_storage_config(config_data.get_data_storage_config())

        strategies_config = {
            name: strategy_data
            for name, strategy_data in config_data.get_strategies_config().items()
        }

        analysis_config = {
            name: analysis_data
            for name, analysis_data in config_data.get_analysis_config().items()
        }

        return AppConfig(cex=cex_config, analysis=analysis_config, data_storage=data_storage_config, strategies=strategies_config)



__all__ = ["ConfigFactory", "CEXConfig", "AnalysisConfig", "StrategyConfig", "AppConfig", "ConfigLoader"]