import os
from datetime import datetime, timedelta
from typing import Dict, List, Union

import pandas as pd
import pytz

from ..config.base import CEXConfig
from ..platform.binance import BinancePlatform
from ..utils.logger import get_logger
from .base import BaseDataCollector

logger = get_logger(__name__)


class BinanceDataCollector(BaseDataCollector):
    def __init__(self, platform: BinancePlatform, config: CEXConfig):
        self.platform = platform
        self.data_dir = os.path.join(config.data_path, "csv_data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.local_tz = pytz.timezone(config.timezone)
        self.utc_tz = pytz.UTC

    def collect_historical_data(
        self,
        symbol: str,
        interval: str,
        start_time: Union[str, datetime],
        end_time: Union[str, datetime],
    ) -> pd.DataFrame:

        start_time_utc = self._to_utc(start_time)
        end_time_utc = self._to_utc(end_time)

        start_time_str = start_time_utc.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = end_time_utc.strftime("%Y-%m-%d %H:%M:%S")

        klines = self.platform.get_historical_klines(
            symbol, interval, start_time_str, end_time_str
        )
        df = self.platform.create_dataframe(klines)
        return self._adjust_timezone(df)

    def _to_utc(self, time: Union[str, datetime]) -> datetime:
        if isinstance(time, str):
            time = pd.to_datetime(time)
        if time.tzinfo is None:
            time = self.local_tz.localize(time)
        return time.astimezone(self.utc_tz)

    def _adjust_timezone(self, df: pd.DataFrame) -> pd.DataFrame:
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)
        df["open_time"] = df["open_time"].dt.tz_convert(self.local_tz)
        df["close_time"] = df["close_time"].dt.tz_convert(self.local_tz)
        return df

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

    def load_data(self, symbol: str, interval: str) -> pd.DataFrame:
        file_path = os.path.join(self.data_dir, symbol, f"{interval}.csv")
        try:
            df = pd.read_csv(file_path, parse_dates=["open_time", "close_time"])
            logger.info(f"Data loaded from {file_path}")
            
            # Convert to timezone-aware datetime if not already
            if df['open_time'].dt.tz is None:
                df["open_time"] = df["open_time"].dt.tz_localize(self.utc_tz).dt.tz_convert(self.local_tz)
                df["close_time"] = df["close_time"].dt.tz_localize(self.utc_tz).dt.tz_convert(self.local_tz)
            else:
                df["open_time"] = df["open_time"].dt.tz_convert(self.local_tz)
                df["close_time"] = df["close_time"].dt.tz_convert(self.local_tz)
            
            return df
        except FileNotFoundError:
            logger.info(f"No existing data found for {symbol} at interval {interval}")
            return pd.DataFrame()


    def save_data(self, data: Dict[str, pd.DataFrame], interval: str) -> None:
        for symbol, df in data.items():
            directory = os.path.join(self.data_dir, symbol)
            os.makedirs(directory, exist_ok=True)
            file_path = os.path.join(directory, f"{interval}.csv")
            df.to_csv(file_path, index=False)
            logger.info(f"Data saved to {file_path}")

    def get_all_usdt_pairs(self) -> List[str]:
        return self.platform.get_all_usdt_pairs()

    def update_data_for_interval(self, interval: str, lookback_days: int = 30) -> None:
        symbols = self.get_all_usdt_pairs()
        end_time = datetime.now(self.local_tz)
        start_time = end_time - timedelta(days=lookback_days)

        for symbol in symbols:
            new_data = self.collect_historical_data(symbol, interval, start_time, end_time)
            if not new_data.empty:
                self.merge_new_data(symbol, interval, new_data)
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
