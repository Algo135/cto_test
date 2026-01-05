from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, List
from datetime import datetime


class Signal:
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    
    def __init__(self, symbol: str, signal_type: str, timestamp: datetime,
                 price: float, quantity: Optional[int] = None, reason: str = ""):
        self.symbol = symbol
        self.signal_type = signal_type
        self.timestamp = timestamp
        self.price = price
        self.quantity = quantity
        self.reason = reason
    
    def __repr__(self):
        return (f"Signal({self.signal_type} {self.symbol} @ {self.price:.2f} "
                f"on {self.timestamp})")


class BaseStrategy(ABC):
    def __init__(self, name: str):
        self.name = name
        self.data = {}
        self.positions = {}
        self.signals = []
    
    @abstractmethod
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> List[Signal]:
        pass
    
    @abstractmethod
    def on_bar(self, bar_event) -> Optional[Signal]:
        pass
    
    def calculate_position_size(self, price: float, capital: float,
                               risk_percent: float = 0.02) -> int:
        position_value = capital * risk_percent
        shares = int(position_value / price)
        return max(1, shares)
    
    def reset(self):
        self.data = {}
        self.positions = {}
        self.signals = []
