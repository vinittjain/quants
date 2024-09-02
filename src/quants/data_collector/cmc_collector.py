import os
from datetime import datetime, timedelta
from typing import Dict, List, Union

import pandas as pd
import pytz

from ..config.base import AppConfig
from ..platform.coinmarketcap import CoinMarketCapPlatform
from ..utils.logger import get_logger
from .base import BaseDataCollector

logger = get_logger(__name__)


class CoinMarketCapDataCollector(BaseDataCollector):
    def __init__(self, platform: CoinMarketCapPlatform, config: AppConfig):
        self.platform = platform
        self.data_dir = os.path.join(config.data_storage.data_path, "csv_data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.local_tz = pytz.timezone(config.cex.timezone)
        self.utc_tz = pytz.UTC

    def collect_historical_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        interval: str = 'daily'
    ) -> pd.DataFrame:
        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
        price_data = self.platform.get_historical_price_data(symbol, start_time_str, end_time_str, interval)
        df = self.platform.create_dataframe(price_data)
        return self._adjust_timezone(df)

    def _adjust_timezone(self, df: pd.DataFrame) -> pd.DataFrame:
        df['timestamp'] = df['timestamp'].dt.tz_localize(self.utc_tz).dt.tz_convert(self.local_tz)
        return df

    def collect_latest_data(self, symbol: str) -> pd.DataFrame:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        return self.collect_historical_data(symbol, start_time, end_time)

    def collect_multiple_symbols(
        self,
        symbols: List[str],
        start_time: datetime,
        end_time: datetime,
        interval: str = 'daily'
    ) -> Dict[str, pd.DataFrame]:
        data = {}
        for symbol in symbols:
            df = self.collect_historical_data(symbol, start_time, end_time, interval)
            if not df.empty:
                data[symbol] = df
        return data

    def load_data(self, symbol: str) -> pd.DataFrame:
        file_path = os.path.join(self.data_dir, f"{symbol}.csv")
        try:
            df = pd.read_csv(file_path, parse_dates=['timestamp'])
            logger.info(f"Data loaded from {file_path}")
            if df['timestamp'].dt.tz is None:
                df['timestamp'] = df['timestamp'].dt.tz_localize(self.utc_tz).dt.tz_convert(self.local_tz)
            else:
                df['timestamp'] = df['timestamp'].dt.tz_convert(self.local_tz)
            return df
        except FileNotFoundError:
            logger.info(f"No existing data found for {symbol}")
            return pd.DataFrame()

    def save_data(self, data: Dict[str, pd.DataFrame]) -> None:
        for symbol, df in data.items():
            file_path = os.path.join(self.data_dir, f"{symbol}.csv")
            df.to_csv(file_path, index=False)
            logger.info(f"Data saved to {file_path}")

    def get_all_cryptocurrencies(self) -> List[Dict[str, Any]]:
        return self.platform.get_all_cryptocurrencies()

    def update_data_for_symbols(self, lookback_days: int = 90) -> None:
        cryptocurrencies = self.get_all_cryptocurrencies()
        end_time = datetime.now()
        start_time = end_time - timedelta(days=lookback_days)
        for crypto in cryptocurrencies:
            symbol = crypto['symbol']
            new_data = self.collect_historical_data(symbol, start_time, end_time)
            if not new_data.empty:
                self.merge_new_data(symbol, new_data)
        logger.info(f"Data updated for all cryptocurrencies")

    def merge_new_data(self, symbol: str, new_data: pd.DataFrame) -> None:
        existing_data = self.load_data(symbol)
        if existing_data.empty:
            merged_data = new_data
        else:
            merged_data = pd.concat([existing_data, new_data]).drop_duplicates(subset=['timestamp']).sort_values('timestamp')
        self.save_data({symbol: merged_data})

    def collect_market_cap_data(self, symbols: List[str]) -> Dict[str, float]:
        market_cap_data = {}
        cryptocurrencies = self.get_all_cryptocurrencies()
        for crypto in cryptocurrencies:
            if crypto['symbol'] in symbols:
                market_cap_data[crypto['symbol']] = crypto['quote']['USD']['market_cap']
        return market_cap_data