import logging
import time

from src.quants.auth import BinanceAuth
from src.quants.config import BinanceConfigLoader
from src.quants.data_collector import BinanceDataCollector
from src.quants.platform import BinancePlatform
from src.quants.task_scheduler import AdvancedTaskScheduler
from src.quants.utils import setup_logging

# Setup logging
logger = setup_logging(log_file="quants.log", log_level=logging.INFO)


def update_interval_data(collector: BinanceDataCollector, interval: str):
    logger.info(f"Starting data update for interval: {interval}")
    collector.update_data_for_interval(interval)
    logger.info(
        f"Data collection and update completed for all USDT pairs for interval: {interval}"
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
            kline_interval=interval,  # Changed from 'interval' to 'kline_interval'
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
