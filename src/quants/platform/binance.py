from typing import Any, Dict, List, Union

import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException

from ..auth.binance import BinanceAuth
from ..utils import get_logger
from .base import BasePlatform

logger = get_logger(__name__)


class BinancePlatform(BasePlatform):
    KLINE_COLS = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume",
        "ignore",
    ]

    KLINE_INTERVALS = {
        "1m": Client.KLINE_INTERVAL_1MINUTE,
        "5m": Client.KLINE_INTERVAL_5MINUTE,
        "1h": Client.KLINE_INTERVAL_1HOUR,
        "4h": Client.KLINE_INTERVAL_4HOUR,
        "6h": Client.KLINE_INTERVAL_6HOUR,
        "8h": Client.KLINE_INTERVAL_8HOUR,
        "1d": Client.KLINE_INTERVAL_1DAY,
    }

    def __init__(self, auth: BinanceAuth):
        self.auth = auth
        self.client = auth.get_client()
        self.spot = auth.get_spot()

    def get_historical_klines(
        self, symbol: str, interval: str, start_time: str, end_time: str
    ) -> List[List[Any]]:

        try:
            return self.client.get_historical_klines(
                symbol, self.KLINE_INTERVALS.get(interval, interval), start_time, end_time
            )
        except BinanceAPIException as e:
            logger.error(f"Failed to fetch historical klines for {symbol}: {e}")
            return []

    def get_exchange_info(self) -> Dict[str, Any]:
        try:
            return self.client.get_exchange_info()
        except BinanceAPIException as e:
            logger.error(f"Failed to fetch exchange info: {e}")
            return {}

    def get_all_usdt_pairs(self) -> List[str]:
        try:
            exchange_info = self.get_exchange_info()
            usdt_pairs = [
                symbol["symbol"]
                for symbol in exchange_info["symbols"]
                if symbol["symbol"].endswith("USDT") and symbol["status"] == "TRADING"
            ]
            logger.info(f"Retrieved {len(usdt_pairs)} USDT trading pairs")
            return usdt_pairs
        except Exception as e:
            logger.error(f"Failed to fetch USDT trading pairs: {e}")
            return []

    @staticmethod
    def create_dataframe(klines: List[List[Any]]) -> pd.DataFrame:
        df = pd.DataFrame(klines, columns=BinancePlatform.KLINE_COLS)
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
        for col in df.columns:
            if col not in ["open_time", "close_time"]:
                df[col] = df[col].astype(float)
        return df

    # You can keep the get_latest_klines method if needed
    def get_latest_klines(
        self, symbol: str, interval: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        try:
            klines = self.spot.klines(
                symbol, self.KLINE_INTERVALS.get(interval, interval), limit=limit
            )
            return [dict(zip(self.KLINE_COLS, kline)) for kline in klines]
        except BinanceAPIException as e:
            logger.error(f"Failed to fetch latest klines for {symbol}: {e}")
            return []
