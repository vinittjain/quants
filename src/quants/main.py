import logging
import time
from typing import Any

from src.quants.analysis_runner import AnalysisRunner
from src.quants.auth import BinanceAuth
from src.quants.data_collector import BinanceDataCollector
from src.quants.platform import BinancePlatform
from src.quants.strategy_runner import StrategyRunner
from src.quants.task_scheduler import AdvancedTaskScheduler
from src.quants.utils.logger import clear_old_logs, get_logger, setup_logging
from src.quants.visualization.chart_drawer import ChartDrawer

from .config import ConfigFactory, ConfigLoader

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
    strategy_runner: StrategyRunner, strategy_name: str, symbol: str, kline_interval: str
):
    logger.info(f"Running {strategy_name} strategy for {symbol} on {kline_interval} interval")
    strategy_runner.run_strategy(strategy_name, symbol, kline_interval)
    logger.info(f"Strategy {strategy_name} completed for {symbol} on {kline_interval} interval")


# def run_analysis(analysis_runner: AnalysisRunner, analysis_name: str, symbols: list[str], interval: str):
#     logger.info(f"Starting analysis: {analysis_name}")
#     result = analysis_runner.run_analysis(analysis_name, symbols, interval)
#     logger.info(f"Analysis {analysis_name} completed. Most influential tokens: {result.get('influential_tokens', [])}")


def main():
    full_config = ConfigLoader(config_path="artifacts/run.yaml")
    app_config = ConfigFactory.create_app_config(full_config)

    auth = BinanceAuth(app_config.cex.api_key, app_config.cex.api_secret)
    platform = BinancePlatform(auth)
    collector = BinanceDataCollector(platform, app_config)

    strategy_runner = StrategyRunner(collector, app_config)
    # analysis_runner = AnalysisRunner(collector, app_config.analysis)
    scheduler = AdvancedTaskScheduler()

    # Schedule analysis tasks
    # for analysis_name in analysis_runner.get_available_analyses():
    #     scheduler.add_task(
    #         name=f"run_analysis_{analysis_name}",
    #         interval="1d",  # Run analysis daily
    #         task=run_analysis,
    #         analysis_runner=analysis_runner,
    #         analysis_name=analysis_name,
    #         symbols=platform.get_all_usdt_pairs(),
    #         interval="1d"  # Use daily data for analysis
    #     )

    # Schedule tasks for each kline interval
    for interval in app_config.cex.kline_intervals:
        scheduler.add_task(
            name=f"update_data_{interval}",
            interval=interval,
            task=update_interval_data,
            collector=collector,
            kline_interval=interval,
        )

    for strategy_name in strategy_runner.get_available_strategies():
        for interval in app_config.cex.kline_intervals:
            for symbol in platform.get_all_usdt_pairs():
                task_name = f"run_strategy_{strategy_name}_{symbol}_{interval}"
                scheduler.add_task(
                    name=task_name,
                    interval=interval,
                    task=run_strategy,
                    runner=strategy_runner,
                    strategy_name=strategy_name,
                    symbol=symbol,
                    kline_interval=interval,
                )
                logger.debug(f"Scheduled task: {task_name}")

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

        for interval in app_config.cex.kline_intervals:
            update_interval_data(collector, interval)

        for strategy_name in strategy_runner.get_available_strategies():
            for interval in app_config.cex.kline_intervals:
                for symbol in platform.get_all_usdt_pairs():
                    run_strategy(strategy_runner, strategy_name, symbol, interval)

        while True:
            time.sleep(60)  # Sleep for 60 seconds
            logger.info("Main thread still running. Scheduler is active.")
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.stop()


if __name__ == "__main__":
    main()
