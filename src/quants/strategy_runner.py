import importlib
import os
from typing import Any, Dict
from hashlib import md5
import pandas as pd

from src.quants.config import AppConfig
from src.quants.db.trigger_log import TriggerLog
from src.quants.strategies.base import BaseStrategy
from src.quants.utils.logger import get_logger
from src.quants.visualization.chart_drawer import ChartDrawer

logger = get_logger(__name__)


class StrategyRunner:
    def __init__(self, collector: Any, config: AppConfig):
        self.collector = collector
        self.config = config
        self.chart_drawer = ChartDrawer(os.path.join(config.data_storage.data_path, "charts"))
        self.trigger_log = TriggerLog(
            os.path.join(config.data_storage.data_path, "trigger_log.db")
        )
        self.strategies = self._load_strategies(config.strategies)

    def _load_strategies(self, strategy_config: Dict[str, Any]) -> Dict[str, BaseStrategy]:
        strategies = {}
        for strategy_name, strategy_params in strategy_config.items():
            try:
                # Convert strategy name to snake_case for module import
                module_name = ''.join(['_' + char.lower() if char.isupper() else char for char in strategy_name]).lstrip('_')
                module = importlib.import_module(f"src.quants.strategies.{module_name}")
                
                # Use the original strategy name for class name
                strategy_class_name = f"{strategy_name}Strategy"
                
                strategy_class = getattr(module, strategy_class_name)
                strategies[strategy_name] = strategy_class(**strategy_params)
                logger.info(f"Successfully loaded strategy: {strategy_name}")
            except (ImportError, AttributeError) as e:
                logger.error(f"Failed to load strategy {strategy_name}: {str(e)}")
        return strategies

    def run_strategy(self, strategy_name: str, symbol: str, interval: str):
        data = self.prepare_data(symbol, interval)

        strategy = self.strategies.get(strategy_name)
        if not strategy:
            logger.error(f"Strategy {strategy_name} not found")
            return

        result = strategy.run(data)

        if result["trigger"]:
            logger.info(f"Trigger condition met for {strategy_name} on {symbol} ({interval})")

            strategy_id = md5(strategy_name.encode()).hexdigest()[:8]
            plot_config = strategy.get_plot_config(result["data"])

            chart_path = self.chart_drawer.draw_chart(
    result["data"], symbol, interval, strategy_id, result["trigger_time"], plot_config
)
            self.trigger_log.log_trigger(
                result["trigger_time"],
                symbol,
                interval,
                strategy_name,
                result["signal"],
                chart_path,
            )

        logger.info(f"Strategy run completed for {strategy_name} on {symbol} ({interval})")

    def prepare_data(self, symbol: str, interval: str) -> pd.DataFrame:
        data = self.collector.load_data(symbol, interval)
        if "close_time" not in data.columns:
            logger.warning("'close_time' column not found in data. Chart dates may be incorrect.")
        return data

    def get_available_strategies(self) -> list[str]:
        return list(self.strategies.keys())
