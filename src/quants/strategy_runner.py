import importlib
import os
from typing import Any, Dict

from .db.trigger_log import TriggerLog
from .strategies.base import BaseStrategy
from .utils.logger import get_logger
from .visualization.chart_drawer import ChartDrawer

logger = get_logger(__name__)


class StrategyRunner:
    def __init__(self, collector, config):
        self.collector = collector
        self.config = config
        self.chart_drawer = ChartDrawer(os.path.join(config.data_path, "charts"))
        self.trigger_log = TriggerLog(os.path.join(config.data_path, "trigger_log.db"))
        self.strategies = self._load_strategies(config.strategies)

    def _load_strategies(self, strategy_config: Dict[str, Any]) -> Dict[str, BaseStrategy]:
        strategies = {}
        for strategy_name, strategy_params in strategy_config.items():
            try:
                module = importlib.import_module(f"src.quants.strategies.{strategy_name.lower()}")
                strategy_class = getattr(module, f"{strategy_name}Strategy")
                strategies[strategy_name] = strategy_class(**strategy_params)
            except (ImportError, AttributeError) as e:
                logger.error(f"Failed to load strategy {strategy_name}: {str(e)}")
        return strategies

    def run_strategy(self, strategy_name: str, symbol: str, interval: str):
        logger.info(f"Running {strategy_name} for {symbol} on {interval} interval")
        data = self.collector.load_data(symbol, interval)
        if data.empty:
            logger.warning(f"No data available for {symbol} on {interval} interval")
            return

        strategy = self.strategies.get(strategy_name)
        if not strategy:
            logger.error(f"Strategy {strategy_name} not found")
            return

        result = strategy.run(data)
        if result["trigger"]:
            logger.info(f"Trigger condition met for {strategy_name} on {symbol} ({interval})")
            chart_path = self.chart_drawer.draw_candlestick(
                data, symbol, interval, strategy_name, result["trigger_time"]
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

    def get_available_strategies(self) -> List[str]:
        return list(self.strategies.keys())
