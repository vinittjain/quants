from binance.client import Client
from binance.spot import Spot

from ..utils import get_logger
from .base import BaseAuth

logger = get_logger(__name__)


class BinanceAuth(BaseAuth):
    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(api_key, api_secret)
        self.spot = Spot()
        logger.info("Binance API initialized")

    def get_client(self) -> Client:
        return self.client

    def get_spot(self) -> Spot:
        return self.spot
