import alpaca_trade_api as tradeapi
from typing import Optional, List
from .broker import Broker
from .order import Order, OrderStatus, OrderType, OrderSide
from src.config import Config


class AlpacaBroker(Broker):
    def __init__(self):
        if not Config.ALPACA_API_KEY or not Config.ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        self.api = tradeapi.REST(
            Config.ALPACA_API_KEY,
            Config.ALPACA_SECRET_KEY,
            Config.ALPACA_BASE_URL,
            api_version='v2'
        )
    
    def submit_order(self, order: Order) -> str:
        try:
            alpaca_order = self.api.submit_order(
                symbol=order.symbol,
                qty=order.quantity,
                side=order.side.value,
                type=order.order_type.value,
                time_in_force=order.time_in_force,
                limit_price=order.price if order.order_type == OrderType.LIMIT else None,
                stop_price=order.stop_price if order.order_type in [OrderType.STOP, OrderType.STOP_LIMIT] else None
            )
            
            order.order_id = alpaca_order.id
            order.status = OrderStatus.SUBMITTED
            
            return alpaca_order.id
        except Exception as e:
            order.status = OrderStatus.REJECTED
            raise RuntimeError(f"Failed to submit order: {str(e)}")
    
    def cancel_order(self, order_id: str) -> bool:
        try:
            self.api.cancel_order(order_id)
            return True
        except Exception as e:
            print(f"Failed to cancel order {order_id}: {str(e)}")
            return False
    
    def get_order_status(self, order_id: str) -> OrderStatus:
        try:
            alpaca_order = self.api.get_order(order_id)
            status_map = {
                'new': OrderStatus.SUBMITTED,
                'accepted': OrderStatus.SUBMITTED,
                'pending_new': OrderStatus.PENDING,
                'filled': OrderStatus.FILLED,
                'partially_filled': OrderStatus.PARTIALLY_FILLED,
                'cancelled': OrderStatus.CANCELLED,
                'rejected': OrderStatus.REJECTED,
                'expired': OrderStatus.CANCELLED
            }
            return status_map.get(alpaca_order.status, OrderStatus.PENDING)
        except Exception as e:
            print(f"Failed to get order status: {str(e)}")
            return OrderStatus.PENDING
    
    def get_account_info(self) -> dict:
        try:
            account = self.api.get_account()
            return {
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'buying_power': float(account.buying_power),
                'equity': float(account.equity),
                'long_market_value': float(account.long_market_value),
                'short_market_value': float(account.short_market_value)
            }
        except Exception as e:
            print(f"Failed to get account info: {str(e)}")
            return {}
    
    def get_positions(self) -> List[dict]:
        try:
            positions = self.api.list_positions()
            return [
                {
                    'symbol': pos.symbol,
                    'quantity': int(pos.qty),
                    'market_value': float(pos.market_value),
                    'avg_entry_price': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_plpc': float(pos.unrealized_plpc)
                }
                for pos in positions
            ]
        except Exception as e:
            print(f"Failed to get positions: {str(e)}")
            return []
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        try:
            barset = self.api.get_latest_trade(symbol)
            return float(barset.price)
        except Exception as e:
            print(f"Failed to get current price for {symbol}: {str(e)}")
            return None
    
    def get_bars(self, symbol: str, timeframe: str = '1Day', limit: int = 100):
        try:
            bars = self.api.get_bars(symbol, timeframe, limit=limit)
            return bars
        except Exception as e:
            print(f"Failed to get bars for {symbol}: {str(e)}")
            return None
