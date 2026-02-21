"""Tests for options Greeks calculations using Black-Scholes model."""

import pytest
import numpy as np

from src.options.greeks import (
    norm_cdf, norm_pdf, calculate_d1, calculate_d2,
    black_scholes_price, delta, gamma, theta, vega, rho,
    Greeks, GreeksCalculator, StrategyGreeks,
    calculate_implied_volatility
)
from src.options.payoff import (
    OptionType, OptionSide, OptionPosition,
    create_long_call, create_long_put, create_long_straddle
)


class TestNormalDistribution:
    """Tests for normal distribution helper functions."""
    
    def test_norm_cdf_zero(self):
        """CDF at 0 should be 0.5."""
        assert norm_cdf(0) == pytest.approx(0.5)
    
    def test_norm_cdf_positive(self):
        """CDF for positive values should be > 0.5."""
        assert norm_cdf(1.96) > 0.5
        assert norm_cdf(1.96) == pytest.approx(0.975, abs=0.001)
    
    def test_norm_cdf_negative(self):
        """CDF for negative values should be < 0.5."""
        assert norm_cdf(-1.96) < 0.5
        assert norm_cdf(-1.96) == pytest.approx(0.025, abs=0.001)
    
    def test_norm_pdf_zero(self):
        """PDF at 0 should be 1/sqrt(2*pi)."""
        expected = 1 / np.sqrt(2 * np.pi)
        assert norm_pdf(0) == pytest.approx(expected)
    
    def test_norm_pdf_symmetry(self):
        """PDF should be symmetric around 0."""
        assert norm_pdf(1) == pytest.approx(norm_pdf(-1))


class TestBlackScholesParameters:
    """Tests for Black-Scholes intermediate calculations."""
    
    def test_d1_calculation(self):
        """d1 calculation should match formula."""
        spot, strike = 100, 100
        tte, r, vol = 0.25, 0.05, 0.20
        
        d1 = calculate_d1(spot, strike, tte, r, vol)
        
        # d1 should be positive when spot > strike*exp(-r*T) with positive vol
        assert d1 > 0
        
        # Verify the formula manually
        expected = (np.log(spot/strike) + (r + 0.5*vol**2)*tte) / (vol*np.sqrt(tte))
        assert d1 == pytest.approx(expected)
    
    def test_d2_calculation(self):
        """d2 should equal d1 - vol*sqrt(T)."""
        d1 = 0.5
        vol, tte = 0.20, 0.25
        
        d2 = calculate_d2(d1, vol, tte)
        expected = d1 - vol * np.sqrt(tte)
        
        assert d2 == pytest.approx(expected)
    
    def test_invalid_volatility(self):
        """Should raise error for non-positive volatility."""
        with pytest.raises(ValueError, match="Volatility must be positive"):
            calculate_d1(100, 100, 0.25, 0.05, 0)
        
        with pytest.raises(ValueError, match="Volatility must be positive"):
            calculate_d1(100, 100, 0.25, 0.05, -0.1)


class TestBlackScholesPricing:
    """Tests for Black-Scholes option pricing."""
    
    def test_call_price_atm(self):
        """ATM call price should be reasonable."""
        price = black_scholes_price(
            spot=100, strike=100, time_to_expiry=0.25,
            risk_free_rate=0.05, volatility=0.20,
            option_type=OptionType.CALL
        )
        
        # ATM call should be positive and roughly proportional to spot*vol*sqrt(T)
        assert price > 0
        assert price < 10  # Sanity check
    
    def test_call_price_itm(self):
        """ITM call should be worth more than intrinsic value."""
        spot, strike = 110, 100
        price = black_scholes_price(
            spot=spot, strike=strike, time_to_expiry=0.25,
            risk_free_rate=0.05, volatility=0.20,
            option_type=OptionType.CALL
        )
        
        intrinsic = spot - strike
        assert price > intrinsic  # Time value should be positive
    
    def test_call_price_otm(self):
        """OTM call should be less than ITM call with same params."""
        otm_price = black_scholes_price(
            spot=90, strike=100, time_to_expiry=0.25,
            risk_free_rate=0.05, volatility=0.20,
            option_type=OptionType.CALL
        )
        
        itm_price = black_scholes_price(
            spot=110, strike=100, time_to_expiry=0.25,
            risk_free_rate=0.05, volatility=0.20,
            option_type=OptionType.CALL
        )
        
        assert otm_price < itm_price
    
    def test_put_call_parity(self):
        """Put-call parity should hold."""
        spot, strike = 100, 100
        tte, r = 0.25, 0.05
        
        call_price = black_scholes_price(
            spot, strike, tte, r, 0.20, OptionType.CALL
        )
        put_price = black_scholes_price(
            spot, strike, tte, r, 0.20, OptionType.PUT
        )
        
        # C - P = S - K*exp(-rT)
        lhs = call_price - put_price
        rhs = spot - strike * np.exp(-r * tte)
        
        assert lhs == pytest.approx(rhs, abs=0.001)
    
    def test_price_at_expiration(self):
        """Price at expiration should equal intrinsic value."""
        for spot in [90, 100, 110]:
            call_price = black_scholes_price(
                spot, 100, 0, 0.05, 0.20, OptionType.CALL
            )
            assert call_price == pytest.approx(max(spot - 100, 0))
            
            put_price = black_scholes_price(
                spot, 100, 0, 0.05, 0.20, OptionType.PUT
            )
            assert put_price == pytest.approx(max(100 - spot, 0))


class TestDelta:
    """Tests for Delta calculation."""
    
    def test_call_delta_range(self):
        """Call delta should be between 0 and 1."""
        for spot in [80, 90, 100, 110, 120]:
            d = delta(spot, 100, 0.25, 0.05, 0.20, OptionType.CALL)
            assert 0 <= d <= 1
    
    def test_put_delta_range(self):
        """Put delta should be between -1 and 0."""
        for spot in [80, 90, 100, 110, 120]:
            d = delta(spot, 100, 0.25, 0.05, 0.20, OptionType.PUT)
            assert -1 <= d <= 0
    
    def test_call_delta_itm(self):
        """Deep ITM call delta should approach 1."""
        d = delta(150, 100, 0.25, 0.05, 0.20, OptionType.CALL)
        assert d > 0.9
    
    def test_call_delta_otm(self):
        """Deep OTM call delta should approach 0."""
        d = delta(50, 100, 0.25, 0.05, 0.20, OptionType.CALL)
        assert d < 0.1
    
    def test_delta_put_call_relationship(self):
        """Put delta should equal call delta minus 1."""
        for spot in [90, 100, 110]:
            call_d = delta(spot, 100, 0.25, 0.05, 0.20, OptionType.CALL)
            put_d = delta(spot, 100, 0.25, 0.05, 0.20, OptionType.PUT)
            assert call_d - put_d == pytest.approx(1.0, abs=0.001)


class TestGamma:
    """Tests for Gamma calculation."""
    
    def test_gamma_positive(self):
        """Gamma should always be positive."""
        for spot in [80, 90, 100, 110, 120]:
            g = gamma(spot, 100, 0.25, 0.05, 0.20)
            assert g > 0
    
    def test_gamma_maximum_atm(self):
        """Gamma should be highest near ATM."""
        gammas = [gamma(s, 100, 0.25, 0.05, 0.20) for s in [80, 90, 100, 110, 120]]
        assert gammas[2] > gammas[0]  # ATM > deep OTM
        assert gammas[2] > gammas[4]  # ATM > deep ITM


class TestTheta:
    """Tests for Theta calculation."""
    
    def test_call_theta_negative(self):
        """Long call theta should typically be negative (time decay)."""
        t = theta(100, 100, 0.25, 0.05, 0.20, OptionType.CALL)
        assert t < 0  # Time decay reduces option value
    
    def test_put_theta_negative(self):
        """Long put theta should typically be negative."""
        t = theta(100, 100, 0.25, 0.05, 0.20, OptionType.PUT)
        assert t < 0


class TestVega:
    """Tests for Vega calculation."""
    
    def test_vega_positive(self):
        """Vega should always be positive."""
        for spot in [80, 90, 100, 110, 120]:
            v = vega(spot, 100, 0.25, 0.05, 0.20)
            assert v > 0
    
    def test_vega_maximum_atm(self):
        """Vega should be highest near ATM."""
        vegas = [vega(s, 100, 0.25, 0.05, 0.20) for s in [80, 90, 100, 110, 120]]
        assert vegas[2] > vegas[0]
        assert vegas[2] > vegas[4]


class TestRho:
    """Tests for Rho calculation."""
    
    def test_call_rho_positive(self):
        """Call rho should be positive."""
        r = rho(100, 100, 0.25, 0.05, 0.20, OptionType.CALL)
        assert r > 0
    
    def test_put_rho_negative(self):
        """Put rho should be negative."""
        r = rho(100, 100, 0.25, 0.05, 0.20, OptionType.PUT)
        assert r < 0


class TestGreeksCalculator:
    """Tests for GreeksCalculator class."""
    
    def test_calculate_all(self):
        """Calculator should return all Greeks."""
        calc = GreeksCalculator(risk_free_rate=0.05, volatility=0.20)
        greeks = calc.calculate_all(
            spot=100, strike=100, time_to_expiry=0.25,
            option_type=OptionType.CALL
        )
        
        assert isinstance(greeks, Greeks)
        assert greeks.delta is not None
        assert greeks.gamma is not None
        assert greeks.theta is not None
        assert greeks.vega is not None
        assert greeks.rho is not None
    
    def test_calculate_for_long_position(self):
        """Calculator should return correct sign for long position."""
        calc = GreeksCalculator(volatility=0.20)
        call = create_long_call(strike=100, premium=5.00)
        
        greeks = calc.calculate_for_position(call, spot=100, time_to_expiry=0.25)
        
        # Long call should have positive delta
        assert greeks.delta > 0
    
    def test_calculate_for_short_position(self):
        """Calculator should invert signs for short position."""
        calc = GreeksCalculator(volatility=0.20)
        
        long_call = create_long_call(strike=100, premium=5.00)
        short_call = OptionPosition(
            strike=100, premium=5.00,
            option_type=OptionType.CALL, side=OptionSide.SHORT
        )
        
        long_greeks = calc.calculate_for_position(long_call, spot=100, time_to_expiry=0.25)
        short_greeks = calc.calculate_for_position(short_call, spot=100, time_to_expiry=0.25)
        
        assert short_greeks.delta == pytest.approx(-long_greeks.delta)
        assert short_greeks.gamma == pytest.approx(-long_greeks.gamma)
    
    def test_missing_volatility(self):
        """Should raise error if volatility not provided."""
        calc = GreeksCalculator()  # No default volatility
        
        with pytest.raises(ValueError, match="Volatility must be provided"):
            calc.calculate_all(spot=100, strike=100, time_to_expiry=0.25,
                              option_type=OptionType.CALL)
    
    def test_to_dict(self):
        """Greeks serialization should work."""
        calc = GreeksCalculator(volatility=0.20)
        greeks = calc.calculate_all(
            spot=100, strike=100, time_to_expiry=0.25,
            option_type=OptionType.CALL
        )
        
        data = greeks.to_dict()
        assert 'delta' in data
        assert 'gamma' in data
        assert 'theta' in data
        assert 'vega' in data
        assert 'rho' in data
        assert 'theta_daily' in data


class TestStrategyGreeks:
    """Tests for StrategyGreeks aggregation."""
    
    def test_straddle_greeks(self):
        """Straddle Greeks should aggregate properly."""
        straddle = create_long_straddle(strike=100, premium_call=3.00, premium_put=2.50)
        
        strategy_greeks = StrategyGreeks(straddle)
        agg = strategy_greeks.calculate(spot=100, time_to_expiry=0.25, volatility=0.20)
        
        # Straddle at ATM should have near-zero delta (delta neutral)
        assert abs(agg.delta) < 0.1
        
        # Gamma and vega should be positive (long both options)
        assert agg.gamma > 0
        assert agg.vega > 0


class TestImpliedVolatility:
    """Tests for implied volatility calculation."""
    
    def test_implied_vol_recovery(self):
        """Should recover original volatility from price."""
        spot, strike, tte, r = 100, 100, 0.25, 0.05
        true_vol = 0.25
        
        # Calculate price with known volatility
        price = black_scholes_price(spot, strike, tte, r, true_vol, OptionType.CALL)
        
        # Recover implied volatility
        implied_vol = calculate_implied_volatility(
            price, spot, strike, tte, r, OptionType.CALL
        )
        
        assert implied_vol == pytest.approx(true_vol, abs=0.001)
    
    def test_implied_vol_different_strikes(self):
        """IV calculation should work for ITM and OTM options."""
        spot, tte, r, true_vol = 100, 0.25, 0.05, 0.30
        
        for strike in [90, 100, 110]:
            price = black_scholes_price(spot, strike, tte, r, true_vol, OptionType.CALL)
            implied = calculate_implied_volatility(
                price, spot, strike, tte, r, OptionType.CALL
            )
            assert implied == pytest.approx(true_vol, abs=0.001)


class TestVectorizedCalculations:
    """Tests for vectorized operations on arrays."""
    
    def test_delta_vectorized(self):
        """Delta should work with numpy arrays."""
        spots = np.array([80, 90, 100, 110, 120])
        deltas = delta(spots, 100, 0.25, 0.05, 0.20, OptionType.CALL)
        
        assert len(deltas) == len(spots)
        assert all(0 <= d <= 1 for d in deltas)
    
    def test_gamma_vectorized(self):
        """Gamma should work with numpy arrays."""
        spots = np.linspace(80, 120, 50)
        gammas = gamma(spots, 100, 0.25, 0.05, 0.20)
        
        assert len(gammas) == len(spots)
        assert all(g > 0 for g in gammas)
