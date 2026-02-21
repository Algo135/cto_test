"""Black-Scholes model for option pricing and Greeks calculations.

This module provides functions for calculating option prices and Greeks
(Delta, Gamma, Theta, Vega, Rho) using the Black-Scholes model for European options.
"""

from dataclasses import dataclass
from typing import Union, Optional
import numpy as np
from scipy.stats import norm

from src.options.payoff import OptionType, OptionPosition, OptionSide, Strategy
from src.config import Config


def norm_cdf(x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Cumulative distribution function of the standard normal distribution.
    
    Args:
        x: Input value(s).
        
    Returns:
        CDF value(s).
    """
    return norm.cdf(x)


def norm_pdf(x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Probability density function of the standard normal distribution.
    
    Args:
        x: Input value(s).
        
    Returns:
        PDF value(s).
    """
    return norm.pdf(x)


def calculate_d1(
    spot: Union[float, np.ndarray],
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float
) -> Union[float, np.ndarray]:
    """Calculate d1 parameter for Black-Scholes formula.
    
    Args:
        spot: Current underlying price.
        strike: Option strike price.
        time_to_expiry: Time to expiration in years.
        risk_free_rate: Annual risk-free interest rate.
        volatility: Annualized volatility.
        
    Returns:
        d1 value(s).
    """
    if volatility <= 0:
        raise ValueError("Volatility must be positive")
    if time_to_expiry < 0:
        raise ValueError("Time to expiry cannot be negative")
    
    # Handle time = 0 case
    if time_to_expiry == 0:
        time_to_expiry = 1e-10
    
    return (np.log(spot / strike) + 
            (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) / \
           (volatility * np.sqrt(time_to_expiry))


def calculate_d2(
    d1: Union[float, np.ndarray],
    volatility: float,
    time_to_expiry: float
) -> Union[float, np.ndarray]:
    """Calculate d2 parameter for Black-Scholes formula.
    
    Args:
        d1: d1 parameter.
        volatility: Annualized volatility.
        time_to_expiry: Time to expiration in years.
        
    Returns:
        d2 value(s).
    """
    return d1 - volatility * np.sqrt(time_to_expiry)


def black_scholes_price(
    spot: Union[float, np.ndarray],
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    option_type: OptionType
) -> Union[float, np.ndarray]:
    """Calculate the theoretical price of a European option using Black-Scholes.
    
    Args:
        spot: Current underlying price.
        strike: Option strike price.
        time_to_expiry: Time to expiration in years.
        risk_free_rate: Annual risk-free interest rate.
        volatility: Annualized volatility.
        option_type: Type of option (CALL or PUT).
        
    Returns:
        Theoretical option price(s).
    """
    if time_to_expiry <= 0:
        # At expiration, price equals intrinsic value
        return np.maximum(spot - strike, 0) if option_type == OptionType.CALL else \
               np.maximum(strike - spot, 0)
    
    d1 = calculate_d1(spot, strike, time_to_expiry, risk_free_rate, volatility)
    d2 = calculate_d2(d1, volatility, time_to_expiry)
    
    if option_type == OptionType.CALL:
        price = spot * norm_cdf(d1) - strike * np.exp(-risk_free_rate * time_to_expiry) * norm_cdf(d2)
    else:  # PUT
        price = strike * np.exp(-risk_free_rate * time_to_expiry) * norm_cdf(-d2) - spot * norm_cdf(-d1)
    
    return price


def delta(
    spot: Union[float, np.ndarray],
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    option_type: OptionType
) -> Union[float, np.ndarray]:
    """Calculate the Delta of an option.
    
    Delta represents the rate of change of the option price with respect to
    the underlying asset price. For calls: N(d1), for puts: N(d1) - 1.
    
    Args:
        spot: Current underlying price.
        strike: Option strike price.
        time_to_expiry: Time to expiration in years.
        risk_free_rate: Annual risk-free interest rate.
        volatility: Annualized volatility.
        option_type: Type of option (CALL or PUT).
        
    Returns:
        Delta value(s).
    """
    if time_to_expiry <= 0:
        # At expiration, delta is either 0 or 1 (call) / -1 (put)
        if option_type == OptionType.CALL:
            return np.where(spot > strike, 1.0, 0.0)
        else:
            return np.where(spot < strike, -1.0, 0.0)
    
    d1 = calculate_d1(spot, strike, time_to_expiry, risk_free_rate, volatility)
    
    if option_type == OptionType.CALL:
        return norm_cdf(d1)
    else:
        return norm_cdf(d1) - 1.0


def gamma(
    spot: Union[float, np.ndarray],
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float
) -> Union[float, np.ndarray]:
    """Calculate the Gamma of an option.
    
    Gamma represents the rate of change of Delta with respect to the underlying
    asset price. Same for calls and puts.
    
    Args:
        spot: Current underlying price.
        strike: Option strike price.
        time_to_expiry: Time to expiration in years.
        risk_free_rate: Annual risk-free interest rate.
        volatility: Annualized volatility.
        
    Returns:
        Gamma value(s).
    """
    if time_to_expiry <= 0:
        return np.zeros_like(spot) if isinstance(spot, np.ndarray) else 0.0
    
    d1 = calculate_d1(spot, strike, time_to_expiry, risk_free_rate, volatility)
    
    return norm_pdf(d1) / (spot * volatility * np.sqrt(time_to_expiry))


def theta(
    spot: Union[float, np.ndarray],
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    option_type: OptionType
) -> Union[float, np.ndarray]:
    """Calculate the Theta of an option (per year).
    
    Theta represents the rate of change of the option price with respect to time.
    Usually expressed as daily decay (divide by 365).
    
    Args:
        spot: Current underlying price.
        strike: Option strike price.
        time_to_expiry: Time to expiration in years.
        risk_free_rate: Annual risk-free interest rate.
        volatility: Annualized volatility.
        option_type: Type of option (CALL or PUT).
        
    Returns:
        Theta value(s) per year (negative for typical decay).
    """
    if time_to_expiry <= 0:
        return np.zeros_like(spot) if isinstance(spot, np.ndarray) else 0.0
    
    d1 = calculate_d1(spot, strike, time_to_expiry, risk_free_rate, volatility)
    d2 = calculate_d2(d1, volatility, time_to_expiry)
    
    common_term = -(spot * norm_pdf(d1) * volatility) / (2 * np.sqrt(time_to_expiry))
    
    if option_type == OptionType.CALL:
        theta_val = common_term - risk_free_rate * strike * np.exp(-risk_free_rate * time_to_expiry) * norm_cdf(d2)
    else:
        theta_val = common_term + risk_free_rate * strike * np.exp(-risk_free_rate * time_to_expiry) * norm_cdf(-d2)
    
    return theta_val


def vega(
    spot: Union[float, np.ndarray],
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float
) -> Union[float, np.ndarray]:
    """Calculate the Vega of an option.
    
    Vega represents the rate of change of the option price with respect to
    volatility (1% change). Same for calls and puts.
    
    Args:
        spot: Current underlying price.
        strike: Option strike price.
        time_to_expiry: Time to expiration in years.
        risk_free_rate: Annual risk-free interest rate.
        volatility: Annualized volatility.
        
    Returns:
        Vega value(s).
    """
    if time_to_expiry <= 0:
        return np.zeros_like(spot) if isinstance(spot, np.ndarray) else 0.0
    
    d1 = calculate_d1(spot, strike, time_to_expiry, risk_free_rate, volatility)
    
    # Vega for 1% change in volatility
    return spot * norm_pdf(d1) * np.sqrt(time_to_expiry) * 0.01


def rho(
    spot: Union[float, np.ndarray],
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    option_type: OptionType
) -> Union[float, np.ndarray]:
    """Calculate the Rho of an option.
    
    Rho represents the rate of change of the option price with respect to
    the risk-free interest rate (1% change).
    
    Args:
        spot: Current underlying price.
        strike: Option strike price.
        time_to_expiry: Time to expiration in years.
        risk_free_rate: Annual risk-free interest rate.
        volatility: Annualized volatility.
        option_type: Type of option (CALL or PUT).
        
    Returns:
        Rho value(s).
    """
    if time_to_expiry <= 0:
        return np.zeros_like(spot) if isinstance(spot, np.ndarray) else 0.0
    
    d1 = calculate_d1(spot, strike, time_to_expiry, risk_free_rate, volatility)
    d2 = calculate_d2(d1, volatility, time_to_expiry)
    
    # Rho for 1% change in interest rate
    if option_type == OptionType.CALL:
        return strike * time_to_expiry * np.exp(-risk_free_rate * time_to_expiry) * norm_cdf(d2) * 0.01
    else:
        return -strike * time_to_expiry * np.exp(-risk_free_rate * time_to_expiry) * norm_cdf(-d2) * 0.01


@dataclass
class Greeks:
    """Container for all Greeks of an option.
    
    Attributes:
        delta: Price sensitivity to underlying.
        gamma: Delta sensitivity to underlying.
        theta: Price sensitivity to time (annual).
        vega: Price sensitivity to volatility (1%).
        rho: Price sensitivity to interest rate (1%).
        spot: Underlying price used for calculation.
        strike: Strike price of the option.
        time_to_expiry: Time to expiration in years.
        volatility: Implied volatility used.
        risk_free_rate: Risk-free rate used.
        option_type: Type of option.
    """
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    spot: float
    strike: float
    time_to_expiry: float
    volatility: float
    risk_free_rate: float
    option_type: OptionType
    
    def to_dict(self) -> dict:
        """Convert Greeks to dictionary."""
        return {
            'delta': self.delta,
            'gamma': self.gamma,
            'theta': self.theta,
            'vega': self.vega,
            'rho': self.rho,
            'theta_daily': self.theta / 365.0,
            'spot': self.spot,
            'strike': self.strike,
            'time_to_expiry': self.time_to_expiry,
            'volatility': self.volatility,
            'risk_free_rate': self.risk_free_rate,
            'option_type': self.option_type.value
        }
    
    def __repr__(self) -> str:
        return (f"Greeks(delta={self.delta:.4f}, gamma={self.gamma:.4f}, "
                f"theta={self.theta:.4f}, vega={self.vega:.4f}, rho={self.rho:.4f})")


class GreeksCalculator:
    """Calculator for option Greeks with configurable parameters."""
    
    def __init__(
        self,
        risk_free_rate: Optional[float] = None,
        volatility: Optional[float] = None
    ):
        """Initialize the calculator.
        
        Args:
            risk_free_rate: Default risk-free rate (uses Config.RISK_FREE_RATE if None).
            volatility: Default volatility (must be provided per calculation if None).
        """
        self.risk_free_rate = risk_free_rate if risk_free_rate is not None else Config.RISK_FREE_RATE
        self.volatility = volatility
    
    def calculate_all(
        self,
        spot: float,
        strike: float,
        time_to_expiry: float,
        option_type: OptionType,
        volatility: Optional[float] = None,
        risk_free_rate: Optional[float] = None
    ) -> Greeks:
        """Calculate all Greeks for an option.
        
        Args:
            spot: Current underlying price.
            strike: Option strike price.
            time_to_expiry: Time to expiration in years.
            option_type: Type of option (CALL or PUT).
            volatility: Annualized volatility (uses default if None).
            risk_free_rate: Annual risk-free rate (uses default if None).
            
        Returns:
            Greeks object with all calculated values.
        """
        vol = volatility if volatility is not None else self.volatility
        rfr = risk_free_rate if risk_free_rate is not None else self.risk_free_rate
        
        if vol is None:
            raise ValueError("Volatility must be provided")
        
        return Greeks(
            delta=delta(spot, strike, time_to_expiry, rfr, vol, option_type),
            gamma=gamma(spot, strike, time_to_expiry, rfr, vol),
            theta=theta(spot, strike, time_to_expiry, rfr, vol, option_type),
            vega=vega(spot, strike, time_to_expiry, rfr, vol),
            rho=rho(spot, strike, time_to_expiry, rfr, vol, option_type),
            spot=spot,
            strike=strike,
            time_to_expiry=time_to_expiry,
            volatility=vol,
            risk_free_rate=rfr,
            option_type=option_type
        )
    
    def calculate_for_position(
        self,
        position: OptionPosition,
        spot: float,
        time_to_expiry: float,
        volatility: Optional[float] = None,
        risk_free_rate: Optional[float] = None
    ) -> Greeks:
        """Calculate Greeks for an OptionPosition.
        
        Args:
            position: The option position.
            spot: Current underlying price.
            time_to_expiry: Time to expiration in years.
            volatility: Annualized volatility.
            risk_free_rate: Annual risk-free rate.
            
        Returns:
            Greeks object (sign-adjusted for long/short position).
        """
        greeks = self.calculate_all(
            spot=spot,
            strike=position.strike,
            time_to_expiry=time_to_expiry,
            option_type=position.option_type,
            volatility=volatility,
            risk_free_rate=risk_free_rate
        )
        
        # Adjust for position side and quantity
        multiplier = position.quantity if position.side == OptionSide.LONG else -position.quantity
        
        return Greeks(
            delta=greeks.delta * multiplier,
            gamma=greeks.gamma * multiplier,
            theta=greeks.theta * multiplier,
            vega=greeks.vega * multiplier,
            rho=greeks.rho * multiplier,
            spot=spot,
            strike=position.strike,
            time_to_expiry=time_to_expiry,
            volatility=volatility or self.volatility or 0.0,
            risk_free_rate=risk_free_rate or self.risk_free_rate,
            option_type=position.option_type
        )


class StrategyGreeks:
    """Aggregated Greeks for a multi-leg option strategy.
    
    This class calculates and stores the combined Greeks for all positions
    in a strategy, properly accounting for long/short positions and quantities.
    """
    
    def __init__(self, strategy: Strategy):
        self.strategy = strategy
        self.position_greeks: list[Greeks] = []
        self.aggregated: Optional[Greeks] = None
    
    def calculate(
        self,
        spot: float,
        time_to_expiry: float,
        volatility: Optional[float] = None,
        risk_free_rate: Optional[float] = None,
        calculator: Optional[GreeksCalculator] = None
    ) -> Greeks:
        """Calculate aggregated Greeks for the entire strategy.
        
        Args:
            spot: Current underlying price.
            time_to_expiry: Time to expiration in years.
            volatility: Annualized volatility.
            risk_free_rate: Annual risk-free rate.
            calculator: Optional pre-configured calculator.
            
        Returns:
            Aggregated Greeks object.
        """
        calc = calculator or GreeksCalculator(risk_free_rate=risk_free_rate, volatility=volatility)
        
        self.position_greeks = []
        total_delta = total_gamma = total_theta = total_vega = total_rho = 0.0
        
        for position in self.strategy.positions:
            greeks = calc.calculate_for_position(position, spot, time_to_expiry, volatility, risk_free_rate)
            self.position_greeks.append(greeks)
            
            total_delta += greeks.delta
            total_gamma += greeks.gamma
            total_theta += greeks.theta
            total_vega += greeks.vega
            total_rho += greeks.rho
        
        self.aggregated = Greeks(
            delta=total_delta,
            gamma=total_gamma,
            theta=total_theta,
            vega=total_vega,
            rho=total_rho,
            spot=spot,
            strike=0,  # Not applicable for strategy
            time_to_expiry=time_to_expiry,
            volatility=volatility or calc.volatility or 0.0,
            risk_free_rate=risk_free_rate or calc.risk_free_rate,
            option_type=OptionType.CALL  # Not applicable for strategy
        )
        
        return self.aggregated
    
    def to_dict(self) -> dict:
        """Convert strategy Greeks to dictionary."""
        return {
            'strategy_name': self.strategy.name,
            'aggregated': self.aggregated.to_dict() if self.aggregated else None,
            'positions': [g.to_dict() for g in self.position_greeks]
        }


def calculate_implied_volatility(
    market_price: float,
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    option_type: OptionType,
    initial_guess: float = 0.2,
    max_iterations: int = 100,
    tolerance: float = 1e-5
) -> float:
    """Calculate implied volatility using Newton-Raphson method.
    
    Args:
        market_price: Observed market price of the option.
        spot: Current underlying price.
        strike: Option strike price.
        time_to_expiry: Time to expiration in years.
        risk_free_rate: Annual risk-free interest rate.
        option_type: Type of option (CALL or PUT).
        initial_guess: Initial volatility estimate.
        max_iterations: Maximum iterations for convergence.
        tolerance: Convergence tolerance.
        
    Returns:
        Implied volatility estimate.
        
    Raises:
        ValueError: If Newton-Raphson fails to converge.
    """
    volatility = initial_guess
    
    for _ in range(max_iterations):
        price = black_scholes_price(spot, strike, time_to_expiry, risk_free_rate, volatility, option_type)
        vega_val = vega(spot, strike, time_to_expiry, risk_free_rate, volatility) * 100  # Convert back from percentage
        
        if abs(vega_val) < 1e-10:
            raise ValueError("Vega too small, cannot calculate implied volatility")
        
        diff = market_price - price
        
        if abs(diff) < tolerance:
            return volatility
        
        volatility += diff / vega_val
        
        if volatility <= 0:
            volatility = 0.001
    
    raise ValueError(f"Failed to converge after {max_iterations} iterations")
