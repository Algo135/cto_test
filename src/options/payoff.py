"""Options payoff calculations for single options and multi-leg strategies.

This module provides classes and functions for calculating option payoffs at expiration,
including single options and complex multi-leg strategies like straddles, spreads,
and condors.
"""

from enum import Enum
from typing import List, Tuple, Optional, Union
import numpy as np
import pandas as pd


class OptionType(Enum):
    """Enumeration for option types."""
    CALL = "call"
    PUT = "put"


class OptionSide(Enum):
    """Enumeration for option position sides."""
    LONG = "long"
    SHORT = "short"


class OptionPosition:
    """Represents a single option position.
    
    Attributes:
        strike: The strike price of the option.
        premium: The premium paid/received for the option.
        quantity: Number of contracts (positive for long, negative for short).
        option_type: Type of option (CALL or PUT).
        side: Position side (LONG or SHORT).
    """
    
    def __init__(
        self,
        strike: float,
        premium: float,
        quantity: int = 1,
        option_type: OptionType = OptionType.CALL,
        side: OptionSide = OptionSide.LONG
    ):
        if strike < 0:
            raise ValueError("Strike price must be positive")
        if premium < 0:
            raise ValueError("Premium cannot be negative")
        if quantity == 0:
            raise ValueError("Quantity cannot be zero")
        
        self.strike = strike
        self.premium = premium
        self.quantity = quantity
        self.option_type = option_type
        self.side = side
    
    def __repr__(self) -> str:
        return (f"OptionPosition({self.side.value} {self.quantity} "
                f"{self.option_type.value} @ ${self.strike:.2f}, "
                f"premium=${self.premium:.2f})")
    
    def to_dict(self) -> dict:
        """Convert position to dictionary for serialization."""
        return {
            'strike': self.strike,
            'premium': self.premium,
            'quantity': self.quantity,
            'option_type': self.option_type.value,
            'side': self.side.value
        }
    
    def payoff_at_expiration(self, underlying_price: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Calculate the payoff at expiration for the given underlying price(s).
        
        Args:
            underlying_price: The underlying price(s) at expiration.
            
        Returns:
            The payoff value(s). Positive for profit, negative for loss.
        """
        if self.option_type == OptionType.CALL:
            intrinsic = np.maximum(underlying_price - self.strike, 0)
        else:  # PUT
            intrinsic = np.maximum(self.strike - underlying_price, 0)
        
        if self.side == OptionSide.LONG:
            return self.quantity * (intrinsic - self.premium)
        else:  # SHORT
            return self.quantity * (self.premium - intrinsic)
    
    def max_profit(self) -> Optional[float]:
        """Calculate the maximum possible profit.
        
        Returns:
            Maximum profit, or None if unlimited.
        """
        if self.side == OptionSide.SHORT:
            return self.quantity * self.premium
        else:  # LONG
            if self.option_type == OptionType.CALL:
                return None  # Unlimited upside
            else:  # PUT
                return self.quantity * (self.strike - self.premium)
    
    def max_loss(self) -> Optional[float]:
        """Calculate the maximum possible loss.
        
        Returns:
            Maximum loss (as positive number), or None if unlimited.
        """
        if self.side == OptionSide.LONG:
            return self.quantity * self.premium
        else:  # SHORT
            if self.option_type == OptionType.CALL:
                return None  # Unlimited loss
            else:  # PUT
                return self.quantity * (self.strike - self.premium)


class Strategy:
    """A multi-leg option strategy composed of multiple OptionPositions.
    
    This class aggregates multiple option positions and provides methods to
    calculate the combined payoff, breakeven points, and max profit/loss.
    
    Attributes:
        name: Name of the strategy.
        positions: List of OptionPosition objects.
    """
    
    def __init__(self, name: str = "Custom Strategy"):
        self.name = name
        self.positions: List[OptionPosition] = []
    
    def __repr__(self) -> str:
        return f"Strategy({self.name}, {len(self.positions)} legs)"
    
    def add_position(self, position: OptionPosition) -> 'Strategy':
        """Add a position to the strategy.
        
        Args:
            position: The OptionPosition to add.
            
        Returns:
            Self for method chaining.
        """
        self.positions.append(position)
        return self
    
    def remove_position(self, index: int) -> 'Strategy':
        """Remove a position from the strategy.
        
        Args:
            index: Index of the position to remove.
            
        Returns:
            Self for method chaining.
        """
        if 0 <= index < len(self.positions):
            self.positions.pop(index)
        return self
    
    def total_payoff(self, underlying_price: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Calculate the total payoff of all positions at expiration.
        
        Args:
            underlying_price: The underlying price(s) at expiration.
            
        Returns:
            The total payoff value(s).
        """
        if not self.positions:
            return 0 if isinstance(underlying_price, (int, float)) else np.zeros_like(underlying_price)
        
        total = sum(pos.payoff_at_expiration(underlying_price) for pos in self.positions)
        return total
    
    def payoff_matrix(
        self,
        min_price: float,
        max_price: float,
        num_points: int = 100
    ) -> pd.DataFrame:
        """Generate a payoff matrix for a range of underlying prices.
        
        Args:
            min_price: Minimum underlying price to evaluate.
            max_price: Maximum underlying price to evaluate.
            num_points: Number of price points to generate.
            
        Returns:
            DataFrame with columns: 'underlying_price', 'total_payoff',
            plus individual position payoffs.
        """
        prices = np.linspace(min_price, max_price, num_points)
        data = {'underlying_price': prices}
        
        for i, pos in enumerate(self.positions):
            data[f'position_{i+1}'] = pos.payoff_at_expiration(prices)
        
        data['total_payoff'] = self.total_payoff(prices)
        
        return pd.DataFrame(data)
    
    def calculate_breakevens(
        self,
        min_price: float,
        max_price: float,
        num_points: int = 1000
    ) -> List[float]:
        """Calculate breakeven price(s) where total payoff equals zero.
        
        Args:
            min_price: Minimum price to search.
            max_price: Maximum price to search.
            num_points: Number of points to evaluate for finding roots.
            
        Returns:
            List of breakeven prices.
        """
        prices = np.linspace(min_price, max_price, num_points)
        payoffs = self.total_payoff(prices)
        
        # Find sign changes (approximate roots)
        breakevens = []
        for i in range(len(prices) - 1):
            if payoffs[i] == 0:
                breakevens.append(prices[i])
            elif payoffs[i] * payoffs[i + 1] < 0:
                # Linear interpolation for better estimate
                p1, p2 = payoffs[i], payoffs[i + 1]
                if abs(p2 - p1) > 1e-10:
                    t = abs(p1) / abs(p2 - p1)
                    breakeven = prices[i] + t * (prices[i + 1] - prices[i])
                    breakevens.append(breakeven)
        
        return breakevens
    
    def max_profit_loss(
        self,
        min_price: float,
        max_price: float,
        num_points: int = 1000
    ) -> Tuple[Optional[float], Optional[float]]:
        """Calculate the maximum profit and loss within a price range.
        
        Args:
            min_price: Minimum price to evaluate.
            max_price: Maximum price to evaluate.
            num_points: Number of points to evaluate.
            
        Returns:
            Tuple of (max_profit, max_loss). Either may be None if unlimited.
        """
        # Sample payoffs in the range
        prices = np.linspace(min_price, max_price, num_points)
        payoffs = self.total_payoff(prices)
        
        # Check if payoffs suggest unlimited profit or loss beyond the range
        # Unlimited profit: payoff keeps increasing as we go toward +infinity
        # Unlimited loss: payoff keeps decreasing (more negative) as we go toward +/-infinity
        
        # Sample at boundaries
        boundary_samples = 20
        left_payoffs = payoffs[:boundary_samples]
        right_payoffs = payoffs[-boundary_samples:]
        
        # Check trend at boundaries (are we in the middle of an ongoing trend?)
        left_trend = np.polyfit(prices[:boundary_samples], left_payoffs, 1)[0]
        right_trend = np.polyfit(prices[-boundary_samples:], right_payoffs, 1)[0]
        
        # Unlimited profit: strongly positive trend at right boundary (going up)
        has_unlimited_profit = right_trend > 0.9
        
        # Unlimited loss: strongly negative trend at either boundary
        # At left: as price -> -infinity, payoff -> -infinity
        # At right: as price -> +infinity, payoff -> -infinity  
        left_unlimited_loss = left_trend > 0.9 and np.min(left_payoffs) < -1.0
        right_unlimited_loss = right_trend < -0.9 and np.min(right_payoffs) < -1.0
        has_unlimited_loss = left_unlimited_loss or right_unlimited_loss
        
        max_profit = np.max(payoffs) if not has_unlimited_profit else None
        max_loss = abs(np.min(payoffs)) if not has_unlimited_loss else None
        
        return max_profit, max_loss
    
    def net_premium(self) -> float:
        """Calculate the net premium paid (positive) or received (negative).
        
        Returns:
            Net premium amount.
        """
        total = 0.0
        for pos in self.positions:
            if pos.side == OptionSide.LONG:
                total -= pos.quantity * pos.premium
            else:
                total += pos.quantity * pos.premium
        return total
    
    def to_dict(self) -> dict:
        """Convert strategy to dictionary for serialization."""
        return {
            'name': self.name,
            'positions': [pos.to_dict() for pos in self.positions],
            'net_premium': self.net_premium()
        }


# Pre-built strategy constructors

def create_long_call(strike: float, premium: float, quantity: int = 1) -> OptionPosition:
    """Create a long call option position."""
    return OptionPosition(strike, premium, quantity, OptionType.CALL, OptionSide.LONG)


def create_short_call(strike: float, premium: float, quantity: int = 1) -> OptionPosition:
    """Create a short call option position."""
    return OptionPosition(strike, premium, quantity, OptionType.CALL, OptionSide.SHORT)


def create_long_put(strike: float, premium: float, quantity: int = 1) -> OptionPosition:
    """Create a long put option position."""
    return OptionPosition(strike, premium, quantity, OptionType.PUT, OptionSide.LONG)


def create_short_put(strike: float, premium: float, quantity: int = 1) -> OptionPosition:
    """Create a short put option position."""
    return OptionPosition(strike, premium, quantity, OptionType.PUT, OptionSide.SHORT)


def create_long_straddle(
    strike: float,
    premium_call: float,
    premium_put: float,
    quantity: int = 1
) -> Strategy:
    """Create a long straddle strategy.
    
    Long straddle involves buying a call and put at the same strike.
    Profits from large moves in either direction.
    """
    strategy = Strategy("Long Straddle")
    strategy.add_position(create_long_call(strike, premium_call, quantity))
    strategy.add_position(create_long_put(strike, premium_put, quantity))
    return strategy


def create_short_straddle(
    strike: float,
    premium_call: float,
    premium_put: float,
    quantity: int = 1
) -> Strategy:
    """Create a short straddle strategy.
    
    Short straddle involves selling a call and put at the same strike.
    Profits from low volatility (price staying near strike).
    """
    strategy = Strategy("Short Straddle")
    strategy.add_position(create_short_call(strike, premium_call, quantity))
    strategy.add_position(create_short_put(strike, premium_put, quantity))
    return strategy


def create_long_strangle(
    strike_low: float,
    strike_high: float,
    premium_put: float,
    premium_call: float,
    quantity: int = 1
) -> Strategy:
    """Create a long strangle strategy.
    
    Long strangle involves buying an OTM put and OTM call.
    Cheaper than straddle but requires larger move to profit.
    """
    strategy = Strategy("Long Strangle")
    strategy.add_position(create_long_put(strike_low, premium_put, quantity))
    strategy.add_position(create_long_call(strike_high, premium_call, quantity))
    return strategy


def create_short_strangle(
    strike_low: float,
    strike_high: float,
    premium_put: float,
    premium_call: float,
    quantity: int = 1
) -> Strategy:
    """Create a short strangle strategy.
    
    Short strangle involves selling an OTM put and OTM call.
    Profits when price stays between strikes.
    """
    strategy = Strategy("Short Strangle")
    strategy.add_position(create_short_put(strike_low, premium_put, quantity))
    strategy.add_position(create_short_call(strike_high, premium_call, quantity))
    return strategy


def create_bull_call_spread(
    strike_low: float,
    strike_high: float,
    premium_low: float,
    premium_high: float,
    quantity: int = 1
) -> Strategy:
    """Create a bull call spread strategy.
    
    Buy call at lower strike, sell call at higher strike.
    Bullish strategy with limited risk and reward.
    """
    strategy = Strategy("Bull Call Spread")
    strategy.add_position(create_long_call(strike_low, premium_low, quantity))
    strategy.add_position(create_short_call(strike_high, premium_high, quantity))
    return strategy


def create_bear_put_spread(
    strike_low: float,
    strike_high: float,
    premium_low: float,
    premium_high: float,
    quantity: int = 1
) -> Strategy:
    """Create a bear put spread strategy.
    
    Buy put at higher strike, sell put at lower strike.
    Bearish strategy with limited risk and reward.
    """
    strategy = Strategy("Bear Put Spread")
    strategy.add_position(create_long_put(strike_high, premium_high, quantity))
    strategy.add_position(create_short_put(strike_low, premium_low, quantity))
    return strategy


def create_long_butterfly(
    center_strike: float,
    wing_width: float,
    premium_low: float,
    premium_mid: float,
    premium_high: float,
    quantity: int = 1
) -> Strategy:
    """Create a long butterfly spread strategy.
    
    Buy one ITM option, sell two ATM options, buy one OTM option.
    Profits when price stays near center strike at expiration.
    """
    strategy = Strategy("Long Butterfly")
    low_strike = center_strike - wing_width
    high_strike = center_strike + wing_width
    
    strategy.add_position(create_long_call(low_strike, premium_low, quantity))
    strategy.add_position(create_short_call(center_strike, premium_mid, quantity * 2))
    strategy.add_position(create_long_call(high_strike, premium_high, quantity))
    return strategy


def create_iron_condor(
    strike_put_low: float,
    strike_put_high: float,
    strike_call_low: float,
    strike_call_high: float,
    premium_put_low: float,
    premium_put_high: float,
    premium_call_low: float,
    premium_call_high: float,
    quantity: int = 1
) -> Strategy:
    """Create an iron condor strategy.
    
    Sell put spread and sell call spread.
    Profits when price stays between the inner strikes.
    """
    strategy = Strategy("Iron Condor")
    
    # Put spread (sell higher strike, buy lower strike)
    strategy.add_position(create_long_put(strike_put_low, premium_put_low, quantity))
    strategy.add_position(create_short_put(strike_put_high, premium_put_high, quantity))
    
    # Call spread (sell lower strike, buy higher strike)
    strategy.add_position(create_short_call(strike_call_low, premium_call_low, quantity))
    strategy.add_position(create_long_call(strike_call_high, premium_call_high, quantity))
    
    return strategy


def create_collar(
    stock_price: float,
    put_strike: float,
    call_strike: float,
    put_premium: float,
    call_premium: float,
    quantity: int = 1
) -> Strategy:
    """Create a collar strategy.
    
    Long stock + long put + short call.
    Protects downside while capping upside.
    """
    strategy = Strategy("Collar")
    
    # Add synthetic stock position as a very deep ITM option
    stock_position = OptionPosition(
        strike=0, premium=stock_price, quantity=quantity,
        option_type=OptionType.CALL, side=OptionSide.LONG
    )
    # Override payoff for stock
    stock_position.payoff_at_expiration = lambda price: quantity * (np.asarray(price) - stock_price)
    
    strategy.add_position(stock_position)
    strategy.add_position(create_long_put(put_strike, put_premium, quantity))
    strategy.add_position(create_short_call(call_strike, call_premium, quantity))
    
    return strategy
