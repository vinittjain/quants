import pandas as pd
import numpy as np
from .base import BaseStrategy

class MomentumStrategy(BaseStrategy):
    def __init__(self, params: dict):
        # super().__init__("Momentum", params)
        self.period = params.get('period', 10)
        self.buy_threshold = params.get('buy_threshold', 0)
        self.sell_threshold = params.get('sell_threshold', 0)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        data['momentum'] = data['close'] - data['close'].shift(self.period)
        return data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self.calculate_indicators(data)
        data['signal'] = np.select(
            [data['momentum'] > self.buy_threshold, data['momentum'] < self.sell_threshold],
            [1, -1],
            default=0
        )
        return data