import os
from .utils.logger import get_logger
from .visualization.chart_drawer import ChartDrawer
from .db.trigger_log import TriggerLog

logger = get_logger(__name__)

class StrategyRunner:
    def __init__(self, collector, strategy_manager, config):
        self.collector = collector
        self.strategy_manager = strategy_manager
        self.config = config
        self.chart_drawer = ChartDrawer(os.path.join(config.data_path, "charts"))
        self.trigger_log = TriggerLog(os.path.join(config.data_path, "trigger_log.db"))

    def run_strategy(self, strategy_name: str, symbol: str, interval: str):
        logger.info(f"Running {strategy_name} for {symbol} on {interval} interval")
        data = self.collector.load_data(symbol, interval)
        if data.empty:
            logger.warning(f"No data available for {symbol} on {interval} interval")
            return

        strategy = self.strategy_manager.get_strategy(strategy_name)
        if not strategy:
            logger.error(f"Strategy {strategy_name} not found")
            return

        result = strategy.run(data)
        if result['trigger']:
            logger.info(f"Trigger condition met for {strategy_name} on {symbol} ({interval})")
            chart_path = self.chart_drawer.draw_candlestick(data, symbol, interval, strategy_name, result['trigger_time'])
            self.trigger_log.log_trigger(result['trigger_time'], symbol, interval, strategy_name, result['signal'], chart_path)

        logger.info(f"Strategy run completed for {strategy_name} on {symbol} ({interval})")