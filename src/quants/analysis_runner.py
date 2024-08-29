import importlib
import os
from typing import Any, Dict

from .utils.logger import get_logger
from .visualization.chart_drawer import ChartDrawer

logger = get_logger(__name__)

class AnalysisRunner:
    def __init__(self, collector, config):
        self.collector = collector
        self.config = config
        self.chart_drawer = ChartDrawer(os.path.join(config.data_path, "analysis_charts"))
        self.analyses = self._load_analyses(config.analysis)

    def _load_analyses(self, analysis_config: Dict[str, Any]) -> Dict[str, Any]:
        analyses = {}
        for analysis_name, analysis_params in analysis_config.items():
            try:
                module = importlib.import_module(f"src.quants.analysis.{analysis_name.lower()}")
                analysis_class = getattr(module, f"{analysis_name}Analysis")
                analyses[analysis_name] = analysis_class(**analysis_params)
            except (ImportError, AttributeError) as e:
                logger.error(f"Failed to load analysis {analysis_name}: {str(e)}")
        return analyses

    def run_analysis(self, analysis_name: str, symbols: list[str], interval: str):
        logger.info(f"Running {analysis_name} for {len(symbols)} symbols on {interval} interval")
        
        analysis = self.analyses.get(analysis_name)
        if not analysis:
            logger.error(f"Analysis {analysis_name} not found")
            return

        # Collect necessary data
        price_data = self.collector.collect_price_data(symbols, interval)
        market_cap_data = self.collector.collect_market_cap_data(symbols)

        # Perform analysis
        result = analysis.perform_analysis(price_data, market_cap_data)

        # Visualize results
        chart_path = os.path.join(self.config.data_path, "analysis_charts", f"{analysis_name}_result.png")
        analysis.visualize(chart_path, result)

        logger.info(f"Analysis {analysis_name} completed. Results saved to {chart_path}")

        return result

    def get_available_analyses(self) -> list[str]:
        return list(self.analyses.keys())