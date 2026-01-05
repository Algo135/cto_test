from abc import ABC, abstractmethod
from typing import Optional, List
from .order import Order, OrderStatus


class Broker(ABC):
    @abstractmethod
    def submit_order(self, order: Order) -> str:
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> OrderStatus:
        pass
    
    @abstractmethod
    def get_account_info(self) -> dict:
        pass
    
    @abstractmethod
    def get_positions(self) -> List[dict]:
        pass
    
    @abstractmethod
    def get_current_price(self, symbol: str) -> Optional[float]:
        pass
