from enum import Enum
from datetime import datetime
from typing import Optional


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Order:
    def __init__(
        self,
        symbol: str,
        order_type: OrderType,
        side: OrderSide,
        quantity: int,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "day"
    ):
        self.order_id = None
        self.symbol = symbol
        self.order_type = order_type
        self.side = side
        self.quantity = quantity
        self.price = price
        self.stop_price = stop_price
        self.time_in_force = time_in_force
        self.status = OrderStatus.PENDING
        self.filled_quantity = 0
        self.filled_price = None
        self.created_at = datetime.now()
        self.filled_at = None
        self.commission = 0.0
    
    def __repr__(self):
        return (f"Order(id={self.order_id}, {self.side.value} {self.quantity} "
                f"{self.symbol} @ {self.price}, status={self.status.value})")
    
    def to_dict(self):
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'order_type': self.order_type.value,
            'side': self.side.value,
            'quantity': self.quantity,
            'price': self.price,
            'stop_price': self.stop_price,
            'status': self.status.value,
            'filled_quantity': self.filled_quantity,
            'filled_price': self.filled_price,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'filled_at': self.filled_at.isoformat() if self.filled_at else None,
            'commission': self.commission
        }


class Fill:
    def __init__(self, order: Order, filled_quantity: int, filled_price: float,
                 timestamp: datetime, commission: float = 0.0):
        self.order = order
        self.filled_quantity = filled_quantity
        self.filled_price = filled_price
        self.timestamp = timestamp
        self.commission = commission
    
    def __repr__(self):
        return (f"Fill({self.order.side.value} {self.filled_quantity} "
                f"{self.order.symbol} @ {self.filled_price:.2f})")
