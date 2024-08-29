from abc import ABC, abstractmethod
from typing import List, Dict
import pandas as pd

class BaseAnalysis(ABC):
    @abstractmethod
    def perform_analysis(self, volume_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def visualize(self, output_path: str):
        pass