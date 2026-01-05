from typing import Optional
from .portfolio import Portfolio
from src.config import Config


class RiskManager:
    def __init__(self, portfolio: Portfolio,
                 max_position_size: float = None,
                 max_drawdown: float = None,
                 max_loss_per_trade: float = 0.02):
        self.portfolio = portfolio
        self.max_position_size = max_position_size or Config.MAX_POSITION_SIZE
        self.max_drawdown = max_drawdown or Config.MAX_DRAWDOWN_THRESHOLD
        self.max_loss_per_trade = max_loss_per_trade
    
    def check_trade(self, symbol: str, quantity: int, price: float, side: str) -> tuple[bool, str]:
        if side.upper() == "BUY":
            return self._check_buy_order(symbol, quantity, price)
        elif side.upper() == "SELL":
            return self._check_sell_order(symbol, quantity)
        return False, "Invalid order side"
    
    def _check_buy_order(self, symbol: str, quantity: int, price: float) -> tuple[bool, str]:
        order_value = quantity * price
        
        if order_value > self.portfolio.cash:
            return False, f"Insufficient cash: need ${order_value:.2f}, have ${self.portfolio.cash:.2f}"
        
        position_size = order_value / self.portfolio.portfolio_value
        if position_size > self.max_position_size:
            return False, f"Position size {position_size:.2%} exceeds max {self.max_position_size:.2%}"
        
        if self.portfolio.get_drawdown() > self.max_drawdown:
            return False, f"Current drawdown {self.portfolio.get_drawdown():.2%} exceeds max {self.max_drawdown:.2%}"
        
        return True, "Trade approved"
    
    def _check_sell_order(self, symbol: str, quantity: int) -> tuple[bool, str]:
        position = self.portfolio.get_position(symbol)
        
        if not position:
            return False, f"No position in {symbol}"
        
        if quantity > position.quantity:
            return False, f"Insufficient shares: trying to sell {quantity}, have {position.quantity}"
        
        return True, "Trade approved"
    
    def calculate_position_size(self, price: float, stop_loss_pct: float = 0.02) -> int:
        risk_amount = self.portfolio.portfolio_value * self.max_loss_per_trade
        
        risk_per_share = price * stop_loss_pct
        
        if risk_per_share == 0:
            return 0
        
        shares = int(risk_amount / risk_per_share)
        
        max_shares = int((self.portfolio.portfolio_value * self.max_position_size) / price)
        
        return min(shares, max_shares)
    
    def should_stop_trading(self) -> tuple[bool, str]:
        drawdown = self.portfolio.get_drawdown()
        
        if drawdown > self.max_drawdown:
            return True, f"Maximum drawdown threshold reached: {drawdown:.2%}"
        
        if self.portfolio.cash < 0:
            return True, "Negative cash balance"
        
        return False, ""
