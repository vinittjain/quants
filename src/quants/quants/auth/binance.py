import logging

from binance.client import Client
from binance.spot import Spot

from .base import BaseAuth


class BinanceAuth(BaseAuth):
    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(api_key, api_secret)
        self.spot = Spot()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Binance API initialized")

    def get_client(self) -> Client:
        return self.client

    def get_spot(self) -> Spot:
        return self.spot
