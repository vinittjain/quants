from .binance_collector import BinanceDataCollector
from .coingecko_collector import CoinGeckoDataCollector
from .coinmarketcap_collector import CoinMarketCapDataCollector

from ..config import AppConfig

__all__ = ["BinanceDataCollector"]


import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta
import pytz
import logging

logger = logging.getLogger(__name__)

class UnifiedDataCollector:
    def __init__(self, binance_collector: BinanceDataCollector, 
                 coingecko_collector: CoinGeckoDataCollector, 
                 coinmarketcap_collector: CoinMarketCapDataCollector,
                 config: AppConfig):
        self.binance_collector = binance_collector
        self.coingecko_collector = coingecko_collector
        self.coinmarketcap_collector = coinmarketcap_collector
        self.config = config
        self.local_tz = pytz.timezone(config.cex.timezone)

    def collect_price_data(self, symbol: str, interval: str, 
                           start_time: datetime, end_time: datetime) -> pd.DataFrame:
        # Collect data from all sources
        binance_data = self.binance_collector.collect_historical_data(
            symbol, interval, start_time, end_time)
        coingecko_data = self.coingecko_collector.collect_historical_data(
            symbol, 'usd', (end_time - start_time).days)
        cmc_data = self.coinmarketcap_collector.collect_historical_data(
            symbol, start_time, end_time)

        # Merge dataframes
        merged_data = self._merge_price_data(binance_data, coingecko_data, cmc_data)
        
        return merged_data

    def _merge_price_data(self, binance_df: pd.DataFrame, 
                          coingecko_df: pd.DataFrame, 
                          cmc_df: pd.DataFrame) -> pd.DataFrame:
        # Ensure all dataframes have a common timestamp column
        binance_df = binance_df.rename(columns={'open_time': 'timestamp'})
        coingecko_df = coingecko_df.rename(columns={'timestamp': 'timestamp'})
        cmc_df = cmc_df.rename(columns={'timestamp': 'timestamp'})

        # Merge dataframes
        merged_df = pd.merge(binance_df, coingecko_df, on='timestamp', how='outer', suffixes=('_binance', '_coingecko'))
        merged_df = pd.merge(merged_df, cmc_df, on='timestamp', how='outer', suffixes=('', '_cmc'))

        # Fill missing values with the average of available values
        price_columns = ['close_binance', 'price_coingecko', 'close_cmc']
        merged_df['unified_price'] = merged_df[price_columns].mean(axis=1)

        return merged_df.sort_values('timestamp')

    def collect_market_cap_data(self, symbols: List[str]) -> Dict[str, float]:
        binance_market_cap = self.binance_collector.collect_market_cap_data(symbols)
        coingecko_market_cap = self.coingecko_collector.collect_market_cap_data(symbols)
        cmc_market_cap = self.coinmarketcap_collector.collect_market_cap_data(symbols)

        unified_market_cap = {}
        for symbol in symbols:
            values = [
                binance_market_cap.get(symbol),
                coingecko_market_cap.get(symbol),
                cmc_market_cap.get(symbol)
            ]
            valid_values = [v for v in values if v is not None]
            if valid_values:
                unified_market_cap[symbol] = sum(valid_values) / len(valid_values)

        return unified_market_cap

    def update_data_for_all_symbols(self, interval: str, lookback_days: int = 90) -> None:
        end_time = datetime.now(self.local_tz)
        start_time = end_time - timedelta(days=lookback_days)

        # Get all symbols from each source
        binance_symbols = set(self.binance_collector.get_all_usdt_pairs())
        coingecko_symbols = set(coin['symbol'] for coin in self.coingecko_collector.get_all_coins())
        cmc_symbols = set(crypto['symbol'] for crypto in self.coinmarketcap_collector.get_all_cryptocurrencies())

        # Combine all symbols
        all_symbols = binance_symbols.union(coingecko_symbols, cmc_symbols)

        for symbol in all_symbols:
            try:
                data = self.collect_price_data(symbol, interval, start_time, end_time)
                if not data.empty:
                    self._save_unified_data(symbol, interval, data)
                logger.info(f"Updated data for {symbol}")
            except Exception as e:
                logger.error(f"Failed to update data for {symbol}: {e}")

    def _save_unified_data(self, symbol: str, interval: str, data: pd.DataFrame) -> None:
        file_path = os.path.join(self.config.data_storage.data_path, f"{symbol}_{interval}_unified.csv")
        data.to_csv(file_path, index=False)
        logger.info(f"Saved unified data for {symbol} to {file_path}")

    def load_unified_data(self, symbol: str, interval: str) -> pd.DataFrame:
        file_path = os.path.join(self.config.data_storage.data_path, f"{symbol}_{interval}_unified.csv")
        try:
            df = pd.read_csv(file_path, parse_dates=['timestamp'])
            logger.info(f"Loaded unified data for {symbol} from {file_path}")
            return df
        except FileNotFoundError:
            logger.info(f"No unified data found for {symbol} at interval {interval}")
            return pd.DataFrame()

    def get_all_symbols(self) -> List[str]:
        binance_symbols = set(self.binance_collector.get_all_usdt_pairs())
        coingecko_symbols = set(coin['symbol'] for coin in self.coingecko_collector.get_all_coins())
        cmc_symbols = set(crypto['symbol'] for crypto in self.coinmarketcap_collector.get_all_cryptocurrencies())
        return list(binance_symbols.union(coingecko_symbols, cmc_symbols))