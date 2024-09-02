import os
from datetime import datetime, timedelta
from typing import Dict, List, Union

import pandas as pd
import pytz

from ..config.base import AppConfig
from ..platform.coin_gecko import CoinGeckoPlatform
from ..utils.logger import get_logger
from .base import BaseDataCollector

logger = get_logger(__name__)

class CoinGeckoDataCollector(BaseDataCollector):
    def __init__(self, platform: CoinGeckoPlatform, config: AppConfig):
        self.platform = platform
        self.data_dir = os.path.join(config.data_storage.data_path, "csv_data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.local_tz = pytz.timezone(config.cex.timezone)
        self.utc_tz = pytz.UTC

    def collect_historical_data(
        self,
        coin_id: str,
        vs_currency: str,
        days: int,
    ) -> pd.DataFrame:
        price_data = self.platform.get_historical_price_data(coin_id, vs_currency, days)
        df = self.platform.create_dataframe(price_data)
        return self._adjust_timezone(df)

    def _adjust_timezone(self, df: pd.DataFrame) -> pd.DataFrame:
        df['timestamp'] = df['timestamp'].dt.tz_localize(self.utc_tz).dt.tz_convert(self.local_tz)
        return df

    def collect_latest_data(self, coin_id: str, vs_currency: str) -> pd.DataFrame:
        price_data = self.platform.get_historical_price_data(coin_id, vs_currency, days=1)
        return self.platform.create_dataframe(price_data)

    def collect_multiple_coins(
        self,
        coin_ids: List[str],
        vs_currency: str,
        days: int,
    ) -> Dict[str, pd.DataFrame]:
        data = {}
        for coin_id in coin_ids:
            df = self.collect_historical_data(coin_id, vs_currency, days)
            if not df.empty:
                data[coin_id] = df
        return data

    def load_data(self, coin_id: str, vs_currency: str) -> pd.DataFrame:
        file_path = os.path.join(self.data_dir, f"{coin_id}_{vs_currency}.csv")
        try:
            df = pd.read_csv(file_path, parse_dates=['timestamp'])
            logger.info(f"Data loaded from {file_path}")
            if df['timestamp'].dt.tz is None:
                df['timestamp'] = df['timestamp'].dt.tz_localize(self.utc_tz).dt.tz_convert(self.local_tz)
            else:
                df['timestamp'] = df['timestamp'].dt.tz_convert(self.local_tz)
            return df
        except FileNotFoundError:
            logger.info(f"No existing data found for {coin_id} vs {vs_currency}")
            return pd.DataFrame()

    def save_data(self, data: Dict[str, pd.DataFrame], vs_currency: str) -> None:
        for coin_id, df in data.items():
            file_path = os.path.join(self.data_dir, f"{coin_id}_{vs_currency}.csv")
            df.to_csv(file_path, index=False)
            logger.info(f"Data saved to {file_path}")

    def get_all_coins(self) -> List[Dict[str, Any]]:
        return self.platform.get_all_coins()

    def update_data_for_coins(self, vs_currency: str, days: int = 90) -> None:
        coins = self.get_all_coins()
        for coin in coins:
            coin_id = coin['id']
            new_data = self.collect_historical_data(coin_id, vs_currency, days)
            if not new_data.empty:
                self.merge_new_data(coin_id, vs_currency, new_data)
        logger.info(f"Data updated for all coins vs {vs_currency}")

    def merge_new_data(self, coin_id: str, vs_currency: str, new_data: pd.DataFrame) -> None:
        existing_data = self.load_data(coin_id, vs_currency)
        if existing_data.empty:
            merged_data = new_data
        else:
            merged_data = pd.concat([existing_data, new_data]).drop_duplicates(subset=['timestamp']).sort_values('timestamp')
        self.save_data({coin_id: merged_data}, vs_currency)

    def collect_market_cap_data(self, coin_ids: List[str]) -> Dict[str, float]:
        market_cap_data = {}
        coins = self.get_all_coins()
        for coin in coins:
            if coin['id'] in coin_ids:
                market_cap_data[coin['id']] = coin['market_cap']
        return market_cap_data