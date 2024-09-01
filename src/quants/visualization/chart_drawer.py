import os
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ChartDrawer:
    def __init__(self, save_dir: str):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def draw_candlestick(
        self,
        data: pd.DataFrame,
        symbol: str,
        interval: str,
        strategy_name: str,
        trigger_time: datetime,
    ):
        logger.info(f"Drawing candlestick chart for {symbol} - {interval} - {strategy_name}")

        if isinstance(trigger_time, (int, float)):
            trigger_time = pd.to_datetime(trigger_time, unit="ms")

        # Ensure trigger_time is timezone-aware
        if trigger_time.tzinfo is None:
            trigger_time = trigger_time.replace(tzinfo=timezone.utc)

        # Prepare the data
        data = data.copy()  # Create a copy to avoid modifying the original data
        if isinstance(data.index[0], (int, float)):
            data.index = pd.to_datetime(data.index, unit="ms")
        data.index = pd.to_datetime(data.index)  # Ensure index is datetime
        data = data.tail(100)  # Last 100 candles

        # Create the plot
        fig, axes = mpf.plot(
            data,
            type="candle",
            style="charles",
            title=f"{symbol} - {interval} - {strategy_name}",
            ylabel="Price",
            volume=True,
            returnfig=True,
            datetime_format="%Y-%m-%d %H:%M",
        )

        # Add trigger indicator
        try:
            trigger_index = data.index.get_loc(trigger_time, method="nearest")
            axes[0].axvline(x=trigger_index, color="r", linestyle="--", label="Trigger")
            logger.debug(f"Trigger added at index {trigger_index}")
        except KeyError:
            logger.warning(
                f"Trigger time {trigger_time} not found in data. Unable to add trigger indicator."
            )

        # Save the plot
        filename = (
            f"{symbol}_{interval}_{strategy_name}_{trigger_time.strftime('%Y%m%d_%H%M%S')}.png"
        )
        filepath = os.path.join(self.save_dir, filename)
        plt.savefig(filepath)
        plt.close(fig)

        logger.info(f"Chart saved to {filepath}")
        return filepath
