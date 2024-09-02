from typing import Any, Dict, List, Union

import pandas as pd
from ..auth import CoinGeckoAuth
from ..utils import get_logger
from .base import BasePlatform

logger = get_logger(__name__)

class CoinGeckoPlatform(BasePlatform):
    def __init__(self, auth: CoinGeckoAuth):
        self.auth = auth
        self.client = auth.get_client()

    def get_historical_price_data(
        self, coin_id: str, vs_currency: str, days: int
    ) -> List[List[Any]]:
        try:
            data = self.client.get_coin_market_chart_by_id(
                id=coin_id, vs_currency=vs_currency, days=days
            )
            return data['prices']
        except Exception as e:
            logger.error(f"Failed to fetch historical price data for {coin_id}: {e}")
            return []

    def get_exchange_info(self) -> Dict[str, Any]:
        try:
            return self.client.get_exchanges_list()
        except Exception as e:
            logger.error(f"Failed to fetch exchange info: {e}")
            return {}

    def get_all_coins(self) -> List[Dict[str, Any]]:
        try:
            coins = self.client.get_coins_markets(vs_currency='usd')
            logger.info(f"Retrieved {len(coins)} coins")
            return coins
        except Exception as e:
            logger.error(f"Failed to fetch coins: {e}")
            return []

    @staticmethod
    def create_dataframe(price_data: List[List[Any]]) -> pd.DataFrame:
        df = pd.DataFrame(price_data, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['price'] = df['price'].astype(float)
        return df