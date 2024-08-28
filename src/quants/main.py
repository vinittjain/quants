import logging
import time
from typing import Any

from src.quants.auth import BinanceAuth
from src.quants.data_collector import BinanceDataCollector
from src.quants.db.trigger_log import TriggerLog
from src.quants.platform import BinancePlatform
from src.quants.strategies import StrategyManager
from src.quants.task_scheduler import AdvancedTaskScheduler
from src.quants.utils.logger import clear_old_logs, get_logger, setup_logging
from src.quants.visualization.chart_drawer import ChartDrawer

from .config import ConfigFactory, ConfigLoader
from .strategy_runner import StrategyRunner

# Setup logging
LOG_DIR = "logs"
setup_logging(log_dir=LOG_DIR, log_level=logging.INFO)
logger = get_logger(__name__)


def update_interval_data(collector: BinanceDataCollector, kline_interval: str):
    logger.info(f"Starting data update for interval: {kline_interval}")
    collector.update_data_for_interval(kline_interval)
    logger.info(
        f"Data collection and update completed for all USDT pairs for interval: {kline_interval}"
    )


def run_strategy(
    collector: BinanceDataCollector,
    strategy_name: str,
    symbol: str,
    kline_interval: str,
    config: Any,
):
    logger.info(f"Running {strategy_name} strategy for {symbol} on {kline_interval} interval")
    data = collector.load_data(symbol, kline_interval)
    if data.empty:
        logger.warning(f"No data available for {symbol} on {kline_interval} interval")
        return

    strategy_manager = StrategyManager(config)
    strategy = strategy_manager.get_strategy(strategy_name)
    if not strategy:
        logger.error(f"Strategy {strategy_name} not found")
        return

    data_with_signals = strategy.generate_signals(data)

    if strategy.check_trigger(data_with_signals):
        logger.info(f"Trigger condition met for {strategy_name} on {symbol} ({kline_interval})")

        chart_drawer = ChartDrawer()
        trigger_time = data_with_signals.index[-1]
        chart_path = chart_drawer.draw_candlestick(
            data_with_signals, symbol, kline_interval, strategy_name, trigger_time
        )

        trigger_log = TriggerLog()
        signal = "BUY" if data_with_signals["signal"].iloc[-1] == 1 else "SELL"
        trigger_log.log_trigger(
            trigger_time, symbol, kline_interval, strategy_name, signal, chart_path
        )
        trigger_log.close()


def main():

    full_config = ConfigLoader(config_path="artifacts/config.yaml")
    app_config = ConfigFactory.create_app_config(full_config)

    auth = BinanceAuth(app_config.cex.api_key, app_config.cex.api_secret)
    platform = BinancePlatform(auth)
    collector = BinanceDataCollector(platform, app_config.cex)
    strategy_manager = StrategyManager(config=app_config.strategies)
    runner = StrategyRunner(collector, app_config.strategies)
    scheduler = AdvancedTaskScheduler()

    for strategy_name, strategy_config in app_config.strategies.items():
        for interval in app_config.cex.kline_intervals:
            for symbol in platform.get_all_usdt_pairs():
                scheduler.add_task(
                    name=f"run_{strategy_name}_{symbol}_{interval}",
                    interval=interval,
                    task=run_strategy,  # You'll need to define this function
                    strategy_name=strategy_name,
                    symbol=symbol,
                    kline_interval=interval,
                )

    # Schedule tasks for each kline interval
    for interval in app_config.cex.kline_intervals:
        scheduler.add_task(
            name=f"update_data_{interval}",
            interval=interval,
            task=update_interval_data,
            collector=collector,
            kline_interval=interval,
        )

    # Schedule log cleaning task
    scheduler.add_task(
        name="clean_old_logs",
        interval="1d",  # Run daily
        task=clear_old_logs,
        log_dir=LOG_DIR,
        days_to_keep=30,
    )

    try:
        scheduler.run()
        logger.info("Scheduler started. Waiting for tasks to run...")

        # Run initial update for all intervals
        for interval in app_config.cex.kline_intervals:
            update_interval_data(collector, interval)

        # for strategy_name, strategy_config in app_config.strategies.items():
        #     for interval in app_config.cex.kline_intervals:
        #         for symbol in platform.get_all_usdt_pairs():
        #             run_strategy(collector, strategy_name, symbol, interval, app_config.strategies)

        while True:
            time.sleep(60)  # Sleep for 60 seconds
            logger.info("Main thread still running. Scheduler is active.")
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.stop()


if __name__ == "__main__":
    main()
