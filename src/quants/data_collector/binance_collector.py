import os
from datetime import datetime, timedelta
from typing import Dict, List, Union

import pandas as pd

from ..platform.binance import BinancePlatform
from ..utils.logger import setup_logging
from .base import BaseDataCollector

logger = setup_logging(__name__)


class BinanceDataCollector(BaseDataCollector):
    def __init__(self, platform: BinancePlatform, base_path: str = "data"):
        self.platform = platform
        self.base_path = base_path

    def collect_historical_data(
        self,
        symbol: str,
        interval: str,
        start_time: Union[str, datetime],
        end_time: Union[str, datetime],
    ) -> pd.DataFrame:
        # Convert datetime to string if necessary
        if isinstance(start_time, datetime):
            start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(end_time, datetime):
            end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

        klines = self.platform.get_historical_klines(symbol, interval, start_time, end_time)
        return self.platform.create_dataframe(klines)

    def collect_latest_data(self, symbol: str, interval: str, limit: int = 100) -> pd.DataFrame:
        klines = self.platform.get_latest_klines(symbol, interval, limit)
        return BinancePlatform.create_dataframe(klines)

    def collect_multiple_symbols(
        self,
        symbols: List[str],
        interval: str,
        start_time: Union[str, datetime],
        end_time: Union[str, datetime],
    ) -> Dict[str, pd.DataFrame]:
        data = {}
        for symbol in symbols:
            df = self.collect_historical_data(symbol, interval, start_time, end_time)
            if not df.empty:
                data[symbol] = df
        return data

    def save_data(self, data: Dict[str, pd.DataFrame], interval: str) -> None:
        for symbol, df in data.items():
            directory = os.path.join(self.base_path, symbol)
            os.makedirs(directory, exist_ok=True)
            file_path = os.path.join(directory, f"{interval}.csv")
            df.to_csv(file_path, index=False)
            logger.info(f"Data saved to {file_path}")

    def load_data(self, symbol: str, interval: str) -> pd.DataFrame:
        file_path = os.path.join(self.base_path, symbol, f"{interval}.csv")
        try:
            return pd.read_csv(file_path, parse_dates=["open_time"])
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return pd.DataFrame()

    def get_all_usdt_pairs(self) -> List[str]:
        return self.platform.get_all_usdt_pairs()

    def update_data_for_interval(self, interval: str, lookback_days: int = 30) -> None:
        symbols = self.get_all_usdt_pairs()
        end_time = datetime.now()
        start_time = end_time - timedelta(days=lookback_days)

        data = self.collect_multiple_symbols(symbols, interval, start_time, end_time)
        self.save_data(data, interval)
        logger.info(f"Data updated for all pairs for interval: {interval}")

    def merge_new_data(self, symbol: str, interval: str, new_data: pd.DataFrame) -> None:
        existing_data = self.load_data(symbol, interval)
        if existing_data.empty:
            merged_data = new_data
        else:
            merged_data = (
                pd.concat([existing_data, new_data])
                .drop_duplicates(subset=["open_time"])
                .sort_values("open_time")
            )

        self.save_data({symbol: merged_data}, interval)

    def get_symbols(self) -> List[str]:
        exchange_info = self.platform.get_exchange_info()
        return [
            s["symbol"]
            for s in exchange_info.get("symbols", [])
            if s["symbol"].endswith("USDT") and s["status"] == "TRADING"
        ]
