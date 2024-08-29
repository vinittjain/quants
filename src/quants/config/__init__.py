from .base import CEXConfig, StrategyConfig, AppConfig, ConfigLoader
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
        return StrategyConfig(name=name, parameters=config_data)

    @staticmethod
    def create_app_config(config_data: Dict[str, Any]) -> AppConfig:
        cex_config = ConfigFactory.create_cex_config(config_data.get_cex_config())
        analysis_config = ConfigFactory.create_analysis_config(config_data.get_analysis_config())
        strategies_config = {
            name: ConfigFactory.create_strategy_config(name, strategy_data)
            for name, strategy_data in config_data.get_strategies_config().items()
        }
        return AppConfig(cex=cex_config, analysis=analysis_config, strategies=strategies_config)



__all__ = ["ConfigFactory", "CEXConfig", "AnalysisConfig", "StrategyConfig", "AppConfig", "ConfigLoader"]