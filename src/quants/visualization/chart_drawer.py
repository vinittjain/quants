import os
from datetime import datetime
from typing import Dict, Any
import pytz

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.ticker as mticker

from ..utils.logger import get_logger

logger = get_logger(__name__)

class ChartDrawer:
    def __init__(self, save_dir: str):
        self.base_save_dir = save_dir
        self.sg_tz = pytz.timezone('Asia/Singapore')

    def draw_chart(
        self,
        data: pd.DataFrame,
        symbol: str,
        interval: str,
        strategy_id: str,
        trigger_time: datetime,
        plot_config: Dict[str, Any]
    ):
        logger.info(f"Drawing chart for {symbol} - {interval} - Strategy ID: {strategy_id}")

        data = data.copy()
        
        # Convert to Singapore timezone
        if 'close_time' in data.columns:
            data['date'] = pd.to_datetime(data['close_time'], unit='ms', utc=True).dt.tz_convert(self.sg_tz)
            data.set_index('date', inplace=True)
        elif not isinstance(data.index, pd.DatetimeIndex):
            if data.index.dtype == 'int64':
                data.index = pd.to_datetime(data.index, unit='ms', utc=True).tz_convert(self.sg_tz)
            else:
                data.index = pd.to_datetime(data.index, utc=True).tz_convert(self.sg_tz)

        # Convert trigger_time to Singapore timezone
        if not isinstance(trigger_time, datetime):
            trigger_time = pd.to_datetime(trigger_time, unit='ms', utc=True)
        if trigger_time.tzinfo is None:
            trigger_time = trigger_time.replace(tzinfo=pytz.UTC)
        trigger_time = trigger_time.astimezone(self.sg_tz)
        
        # Ensure we have a valid trigger_time
        if trigger_time.year == 1970:
            logger.warning("Invalid trigger_time detected. Using current time instead.")
            trigger_time = datetime.now(self.sg_tz)
        
        data = data.tail(100)  # Last 100 candles
        data = data.sort_index()

        # Validate data
        if len(data) == 0:
            logger.error("No data to plot")
            return None
        
        if len(data.index.unique()) != len(data):
            logger.warning("Duplicate index values found. Keeping only the last occurrence.")
            data = data[~data.index.duplicated(keep='last')]

        # Create subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 16), sharex=True, gridspec_kw={'height_ratios': [3, 1, 1]})
        
        # Plot candlestick chart
        ohlc = data[['open', 'high', 'low', 'close']].reset_index()
        ohlc['date'] = mdates.date2num(ohlc['date'].dt.to_pydatetime())
        candlestick_ohlc(ax1, ohlc.values, width=0.6, colorup='g', colordown='r')
        
        # Plot volume
        ax2.bar(data.index, data['volume'], color='b', alpha=0.5)
        ax2.set_ylabel('Volume')

        # Plot indicators
        for indicator in plot_config['indicator_columns']:
            if indicator in data.columns:
                ax3.plot(data.index, data[indicator], label=indicator)
            else:
                logger.warning(f"Indicator {indicator} not found in data")
        ax3.legend()
        ax3.set_ylabel('Indicators')

        # Add trigger line
        for ax in [ax1, ax2, ax3]:
            ax.axvline(x=trigger_time, color='purple', linestyle='--', linewidth=1)

        # Format x-axis
        for ax in [ax1, ax2, ax3]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        plt.xticks(rotation=45)

        # Set titles and labels
        ax1.set_title(f'{symbol} - {interval}')
        ax1.set_ylabel('Price')
        
        # Adjust y-axis for better visibility
        for ax in [ax1, ax2, ax3]:
            ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='both'))

        # Ensure data spans the entire x-axis
        for ax in [ax1, ax2, ax3]:
            ax.set_xlim(data.index.min(), data.index.max())

        plt.tight_layout()

        # Create directory structure and save the plot
        current_date = trigger_time.strftime('%Y-%m-%d')
        save_dir = os.path.join(self.base_save_dir, current_date, strategy_id, symbol)
        os.makedirs(save_dir, exist_ok=True)
        
        filename = f"{trigger_time.strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(save_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)

        logger.info(f"Chart saved to {filepath}")
        return filepath