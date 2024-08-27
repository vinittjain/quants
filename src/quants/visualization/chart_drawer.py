import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime
import os
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ChartDrawer:
    def __init__(self, save_dir: str = 'trigger_charts'):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        logger.info(f"ChartDrawer initialized with save directory: {save_dir}")

    def draw_candlestick(self, data: pd.DataFrame, symbol: str, interval: str, strategy_name: str, trigger_time: datetime):
        logger.info(f"Drawing candlestick chart for {symbol} - {interval} - {strategy_name}")
        
        # Prepare the data
        data = data.set_index('open_time')
        data.index.name = 'Date'
        data = data.tail(100)  # Last 100 candles
        
        # Create the plot
        fig, axes = mpf.plot(data, type='candle', style='charles',
                             title=f'{symbol} - {interval} - {strategy_name}',
                             ylabel='Price',
                             volume=True,
                             returnfig=True)

        # Add trigger indicator
        trigger_index = data.index.get_loc(trigger_time, method='nearest')
        axes[0].axvline(x=trigger_index, color='r', linestyle='--', label='Trigger')

        # Save the plot
        filename = f"{symbol}_{interval}_{strategy_name}_{trigger_time.strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.save_dir, filename)
        plt.savefig(filepath)
        plt.close(fig)

        logger.info(f"Chart saved to {filepath}")
        return filepath