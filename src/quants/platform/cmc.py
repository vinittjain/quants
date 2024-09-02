from typing import Any, Dict, List, Union

import pandas as pd

from ..auth.coinmarketcap import CoinMarketCapAuth
from ..utils import get_logger
from .base import BasePlatform

logger = get_logger(__name__)

class CoinMarketCapPlatform(BasePlatform):
    def __init__(self, auth: CoinMarketCapAuth):
        self.auth = auth
        self.session = auth.get_session()
        self.base_url = auth.base_url

    def _make_request(self, endpoint: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        url = self.base_url + endpoint
        try:
            response = self.session.get(url, params=parameters)
            data = json.loads(response.text)
            return data
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            logger.error(f"Error making request to {endpoint}: {e}")
            return {}

    def get_historical_price_data(
        self, symbol: str, time_start: str, time_end: str, interval: str = 'daily'
    ) -> List[Dict[str, Any]]:
        endpoint = 'cryptocurrency/ohlcv/historical'
        parameters = {
            'symbol': symbol,
            'time_start': time_start,
            'time_end': time_end,
            'interval': interval
        }
        data = self._make_request(endpoint, parameters)
        return data.get('data', {}).get('quotes', [])

    def get_exchange_info(self) -> Dict[str, Any]:
        endpoint = 'exchange/info'
        return self._make_request(endpoint)

    def get_all_cryptocurrencies(self, limit: int = 5000) -> List[Dict[str, Any]]:
        endpoint = 'cryptocurrency/listings/latest'
        parameters = {
            'start': '1',
            'limit': str(limit),
            'convert': 'USD'
        }
        data = self._make_request(endpoint, parameters)
        return data.get('data', [])

    @staticmethod
    def create_dataframe(price_data: List[Dict[str, Any]]) -> pd.DataFrame:
        df = pd.DataFrame(price_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        return df