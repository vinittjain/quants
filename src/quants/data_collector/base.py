from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List

import pandas as pd


class BaseDataCollector(ABC):
    @abstractmethod
    def collect_historical_data(
        self, symbol: str, interval: str, start_time: datetime, end_time: datetime
    ) -> pd.DataFrame:
        """
        Collect historical data for a given symbol and time range.

        :param symbol: The trading symbol (e.g., 'BTCUSDT')
        :param interval: The candlestick interval (e.g., '1h', '4h', '1d')
        :param start_time: The start time for the data collection
        :param end_time: The end time for the data collection
        :return: A DataFrame containing the collected data
        """
        pass

    @abstractmethod
    def collect_latest_data(self, symbol: str, interval: str, limit: int) -> pd.DataFrame:
        """
        Collect the latest data for a given symbol.

        :param symbol: The trading symbol (e.g., 'BTCUSDT')
        :param interval: The candlestick interval (e.g., '1h', '4h', '1d')
        :param limit: The number of latest candles to retrieve
        :return: A DataFrame containing the collected data
        """
        pass

    @abstractmethod
    def collect_multiple_symbols(
        self, symbols: List[str], interval: str, start_time: datetime, end_time: datetime
    ) -> Dict[str, pd.DataFrame]:
        """
        Collect historical data for multiple symbols.

        :param symbols: A list of trading symbols
        :param interval: The candlestick interval (e.g., '1h', '4h', '1d')
        :param start_time: The start time for the data collection
        :param end_time: The end time for the data collection
        :return: A dictionary with symbols as keys and DataFrames as values
        """
        pass

    @abstractmethod
    def save_data(self, data: Dict[str, pd.DataFrame], base_path: str) -> None:
        """
        Save the collected data to a specified location.

        :param data: A dictionary with symbols as keys and DataFrames as values
        :param base_path: The base path where the data should be saved
        """
        pass

    @abstractmethod
    def load_data(self, symbol: str, interval: str, base_path: str) -> pd.DataFrame:
        """
        Load previously saved data for a given symbol and interval.

        :param symbol: The trading symbol (e.g., 'BTCUSDT')
        :param interval: The candlestick interval (e.g., '1h', '4h', '1d')
        :param base_path: The base path where the data is saved
        :return: A DataFrame containing the loaded data
        """
        pass

    @abstractmethod
    def get_symbols(self) -> List[str]:
        """
        Get a list of available trading symbols.

        :return: A list of trading symbols
        """
        pass
