import logging
import time

from src.quants.auth import BinanceAuth
from src.quants.config import BinanceConfigLoader
from src.quants.data_collector import BinanceDataCollector
from src.quants.platform import BinancePlatform
from src.quants.task_scheduler import AdvancedTaskScheduler
from src.quants.utils.logger import clear_old_logs, get_logger, setup_logging

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


def main():
    config_loader = BinanceConfigLoader()
    config = config_loader.load_config("artifacts/config.yaml")

    auth = BinanceAuth(config.api_key, config.api_secret)
    platform = BinancePlatform(auth)
    collector = BinanceDataCollector(platform, base_path=config.data_path)
    scheduler = AdvancedTaskScheduler()

    # Schedule tasks for each kline interval
    for interval in config.kline_intervals:
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
        for interval in config.kline_intervals:
            update_interval_data(collector, interval)

        while True:
            time.sleep(60)  # Sleep for 60 seconds
            logger.info("Main thread still running. Scheduler is active.")
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.stop()


if __name__ == "__main__":
    main()
