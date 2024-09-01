from abc import ABC, abstractmethod
from datetime import datetime, timezone
import pandas as pd


class BaseStrategy(ABC):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    def run(self, data: pd.DataFrame) -> dict:
        data = self.generate_signals(data)

        last_signal = data["signal"].iloc[-1]
        trigger = last_signal != 0

        return {
            "trigger": trigger,
            "signal": "BUY" if last_signal > 0 else "SELL" if last_signal < 0 else "HOLD",
            "trigger_time": data.index[-1],
            "data": data,
        }
