from abc import ABC, abstractmethod
import pandas as pd

class TradingModel(ABC):
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.model = None

    @abstractmethod
    def preprocess(self):
        pass

    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def predict(self, X):
        pass

    @abstractmethod
    def evaluate(self, X, y):
        pass
