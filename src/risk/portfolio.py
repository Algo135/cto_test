from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class Position:
    def __init__(self, symbol: str, quantity: int, avg_price: float):
        self.symbol = symbol
        self.quantity = quantity
        self.avg_price = avg_price
        self.current_price = avg_price
        self.market_value = quantity * avg_price
        self.unrealized_pl = 0.0
    
    def update_price(self, current_price: float):
        self.current_price = current_price
        self.market_value = self.quantity * current_price
        self.unrealized_pl = (current_price - self.avg_price) * self.quantity
    
    def __repr__(self):
        return f"Position({self.symbol}: {self.quantity} @ {self.avg_price:.2f})"


class Trade:
    def __init__(self, symbol: str, side: str, quantity: int, price: float,
                 timestamp: datetime, commission: float = 0.0):
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp
        self.commission = commission
        self.pnl = 0.0
    
    def __repr__(self):
        return f"Trade({self.side} {self.quantity} {self.symbol} @ {self.price:.2f})"


class Portfolio:
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve = []
        self.portfolio_value = initial_capital
        self.peak_value = initial_capital
    
    def update_position(self, symbol: str, quantity: int, price: float,
                       side: str, commission: float = 0.0):
        timestamp = datetime.now()
        trade = Trade(symbol, side, quantity, price, timestamp, commission)
        self.trades.append(trade)
        
        if side.upper() == "BUY":
            if symbol in self.positions:
                pos = self.positions[symbol]
                total_cost = (pos.quantity * pos.avg_price) + (quantity * price)
                total_quantity = pos.quantity + quantity
                pos.quantity = total_quantity
                pos.avg_price = total_cost / total_quantity if total_quantity > 0 else 0
            else:
                self.positions[symbol] = Position(symbol, quantity, price)
            
            self.cash -= (quantity * price + commission)
        
        elif side.upper() == "SELL":
            if symbol in self.positions:
                pos = self.positions[symbol]
                if quantity >= pos.quantity:
                    realized_pl = (price - pos.avg_price) * pos.quantity
                    trade.pnl = realized_pl - commission
                    del self.positions[symbol]
                else:
                    realized_pl = (price - pos.avg_price) * quantity
                    trade.pnl = realized_pl - commission
                    pos.quantity -= quantity
                
                self.cash += (quantity * price - commission)
            else:
                print(f"Warning: Attempting to sell {symbol} without position")
    
    def update_prices(self, prices: Dict[str, float]):
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].update_price(price)
        
        self._calculate_portfolio_value()
    
    def _calculate_portfolio_value(self):
        positions_value = sum(pos.market_value for pos in self.positions.values())
        self.portfolio_value = self.cash + positions_value
        
        if self.portfolio_value > self.peak_value:
            self.peak_value = self.portfolio_value
        
        self.equity_curve.append({
            'timestamp': datetime.now(),
            'value': self.portfolio_value,
            'cash': self.cash,
            'positions_value': positions_value
        })
    
    def get_position(self, symbol: str) -> Optional[Position]:
        return self.positions.get(symbol)
    
    def has_position(self, symbol: str) -> bool:
        return symbol in self.positions
    
    def get_total_return(self) -> float:
        return (self.portfolio_value - self.initial_capital) / self.initial_capital
    
    def get_drawdown(self) -> float:
        if self.peak_value == 0:
            return 0.0
        return (self.peak_value - self.portfolio_value) / self.peak_value
    
    def get_summary(self) -> dict:
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]
        
        return {
            'initial_capital': self.initial_capital,
            'cash': self.cash,
            'portfolio_value': self.portfolio_value,
            'total_return': self.get_total_return(),
            'total_return_pct': self.get_total_return() * 100,
            'peak_value': self.peak_value,
            'drawdown': self.get_drawdown(),
            'drawdown_pct': self.get_drawdown() * 100,
            'num_positions': len(self.positions),
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / total_trades if total_trades > 0 else 0,
            'avg_win': sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0,
            'avg_loss': sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        }
