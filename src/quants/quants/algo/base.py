from abc import ABC, abstractmethod

import pandas as pd


class BaseAlgorithm(ABC):
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> str:
        """
        Generate a trading signal based on the given data.

        :param data: DataFrame containing market data
        :return: A string representing the signal ('BUY', 'SELL', or 'HOLD')
        """
        pass
