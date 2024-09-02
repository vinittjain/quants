
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

from ..utils import get_logger
from .base import BaseAuth

logger = get_logger(__name__)

class CoinMarketCapAuth(BaseAuth):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://pro-api.coinmarketcap.com/v1/'
        self.session = Session()
        self.session.headers.update({
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': api_key,
        })
        logger.info("CoinMarketCap API initialized")

    def get_session(self) -> Session:
        return self.session
