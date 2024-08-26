from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union


class BasePlatform(ABC):
    @abstractmethod
    def get_historical_klines(
        self, symbol: str, interval: str, start_time: str, end_time: str
    ) -> List[List[Any]]:
        pass

    @abstractmethod
    def get_exchange_info(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_all_usdt_pairs(self) -> List[str]:
        pass
