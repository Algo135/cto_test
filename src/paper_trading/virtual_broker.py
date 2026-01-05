import uuid
from datetime import datetime
from typing import Optional, List, Dict
from src.execution.broker import Broker
from src.execution.order import Order, OrderStatus, OrderSide
from src.risk.portfolio import Portfolio
from src.config import Config


class VirtualBroker(Broker):
    def __init__(self, initial_capital: float = None):
        self.initial_capital = initial_capital or Config.INITIAL_CAPITAL
        self.portfolio = Portfolio(self.initial_capital)
        self.orders: Dict[str, Order] = {}
        self.current_prices: Dict[str, float] = {}
    
    def submit_order(self, order: Order) -> str:
        order.order_id = str(uuid.uuid4())
        order.status = OrderStatus.SUBMITTED
        self.orders[order.order_id] = order
        
        self._execute_order(order)
        
        return order.order_id
    
    def _execute_order(self, order: Order):
        if order.symbol not in self.current_prices:
            order.status = OrderStatus.REJECTED
            return
        
        execution_price = self.current_prices[order.symbol]
        
        if order.side == OrderSide.BUY:
            execution_price *= (1 + Config.SLIPPAGE_PERCENT)
        else:
            execution_price *= (1 - Config.SLIPPAGE_PERCENT)
        
        order.filled_price = execution_price
        order.filled_quantity = order.quantity
        order.filled_at = datetime.now()
        order.commission = Config.COMMISSION_PER_TRADE
        order.status = OrderStatus.FILLED
        
        self.portfolio.update_position(
            order.symbol,
            order.quantity,
            execution_price,
            order.side.value,
            order.commission
        )
    
    def cancel_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            order = self.orders[order_id]
            if order.status in [OrderStatus.PENDING, OrderStatus.SUBMITTED]:
                order.status = OrderStatus.CANCELLED
                return True
        return False
    
    def get_order_status(self, order_id: str) -> OrderStatus:
        if order_id in self.orders:
            return self.orders[order_id].status
        return OrderStatus.REJECTED
    
    def get_account_info(self) -> dict:
        return {
            'cash': self.portfolio.cash,
            'portfolio_value': self.portfolio.portfolio_value,
            'buying_power': self.portfolio.cash,
            'equity': self.portfolio.portfolio_value,
            'initial_capital': self.initial_capital,
            'total_return': self.portfolio.get_total_return(),
            'drawdown': self.portfolio.get_drawdown()
        }
    
    def get_positions(self) -> List[dict]:
        return [
            {
                'symbol': pos.symbol,
                'quantity': pos.quantity,
                'avg_entry_price': pos.avg_price,
                'current_price': pos.current_price,
                'market_value': pos.market_value,
                'unrealized_pl': pos.unrealized_pl
            }
            for pos in self.portfolio.positions.values()
        ]
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        return self.current_prices.get(symbol)
    
    def update_prices(self, prices: Dict[str, float]):
        self.current_prices.update(prices)
        self.portfolio.update_prices(prices)
