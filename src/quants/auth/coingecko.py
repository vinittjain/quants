from pycoingecko import CoinGeckoAPI
from ..utils import get_logger
from .base import BaseAuth

logger = get_logger(__name__)

class CoinGeckoAuth(BaseAuth):
    def __init__(self, api_key: str = None):
        self.client = CoinGeckoAPI(api_key=api_key)
        logger.info("CoinGecko API initialized")

    def get_client(self) -> CoinGeckoAPI:
        return self.client