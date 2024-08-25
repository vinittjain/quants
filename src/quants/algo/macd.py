import logging

import pandas as pd

from .base import BaseAlgorithm


class MACDAlgorithm(BaseAlgorithm):
    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.logger = logging.getLogger(__name__)

    def generate_signal(self, data: pd.DataFrame) -> str:
        if len(data) < self.slow_period:
            return "HOLD"

        # Calculate MACD
        exp1 = data["close"].ewm(span=self.fast_period, adjust=False).mean()
        exp2 = data["close"].ewm(span=self.slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=self.signal_period, adjust=False).mean()

        # Generate signal
        if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
            self.logger.info(
                f"BUY signal: MACD ({macd.iloc[-1]:.2f}) crossed above "
                f"Signal ({signal.iloc[-1]:.2f})"
            )
            return "BUY"
        elif macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]:
            self.logger.info(
                f"SELL signal: MACD ({macd.iloc[-1]:.2f}) crossed below "
                f"Signal ({signal.iloc[-1]:.2f})"
            )
            return "SELL"
        else:
            return "HOLD"
