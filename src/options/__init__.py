"""Options Analytics Module

This module provides tools for options payoff analysis, Greeks calculations,
and visualization for the algorithmic trading system.

Core Components:
    - payoff: Option position representation and payoff calculations
    - greeks: Black-Scholes model and Greeks calculations
    - visualization: Plotting utilities for payoffs and Greeks

Example Usage:
    >>> from src.options import create_long_straddle, GreeksCalculator
    >>> 
    >>> # Create a straddle strategy
    >>> straddle = create_long_straddle(
    ...     strike=100,
    ...     premium_call=2.50,
    ...     premium_put=2.50
    ... )
    >>> 
    >>> # Calculate payoff matrix
    >>> matrix = straddle.payoff_matrix(80, 120, 50)
    >>> print(matrix[['underlying_price', 'total_payoff']].head())
    >>> 
    >>> # Calculate Greeks
    >>> calc = GreeksCalculator(volatility=0.20)
    >>> greeks = calc.calculate_for_position(
    ...     straddle.positions[0],  # Call leg
    ...     spot=100,
    ...     time_to_expiry=30/365
    ... )
    >>> print(greeks)
"""

from src.options.payoff import (
    OptionType,
    OptionSide,
    OptionPosition,
    Strategy,
    create_long_call,
    create_short_call,
    create_long_put,
    create_short_put,
    create_long_straddle,
    create_short_straddle,
    create_long_strangle,
    create_short_strangle,
    create_bull_call_spread,
    create_bear_put_spread,
    create_long_butterfly,
    create_iron_condor,
    create_collar,
)

from src.options.greeks import (
    Greeks,
    GreeksCalculator,
    StrategyGreeks,
    black_scholes_price,
    delta,
    gamma,
    theta,
    vega,
    rho,
    calculate_implied_volatility,
)

from src.options.visualization import (
    PayoffPlotter,
    GreeksPlotter,
    StrategyPlotter,
)

__version__ = "1.0.0"
__all__ = [
    # Enums
    "OptionType",
    "OptionSide",
    # Core classes
    "OptionPosition",
    "Strategy",
    "Greeks",
    "GreeksCalculator",
    "StrategyGreeks",
    # Visualization
    "PayoffPlotter",
    "GreeksPlotter",
    "StrategyPlotter",
    # Payoff functions
    "create_long_call",
    "create_short_call",
    "create_long_put",
    "create_short_put",
    "create_long_straddle",
    "create_short_straddle",
    "create_long_strangle",
    "create_short_strangle",
    "create_bull_call_spread",
    "create_bear_put_spread",
    "create_long_butterfly",
    "create_iron_condor",
    "create_collar",
    # Greeks functions
    "black_scholes_price",
    "delta",
    "gamma",
    "theta",
    "vega",
    "rho",
    "calculate_implied_volatility",
]
