from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List


class BasePlatform(ABC):
    @abstractmethod
    def get_historical_klines(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime,
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_exchange_info(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_all_usdt_pairs(self) -> List[str]:
        pass
