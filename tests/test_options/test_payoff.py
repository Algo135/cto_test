"""Tests for options payoff calculations."""

import pytest
import numpy as np

from src.options.payoff import (
    OptionType, OptionSide, OptionPosition, Strategy,
    create_long_call, create_short_call, create_long_put, create_short_put,
    create_long_straddle, create_short_straddle, create_long_strangle,
    create_bull_call_spread, create_bear_put_spread, create_long_butterfly,
    create_iron_condor
)


class TestOptionPosition:
    """Tests for OptionPosition class."""
    
    def test_long_call_payoff_itm(self):
        """Long call should have positive payoff when ITM."""
        call = create_long_call(strike=100, premium=5.00)
        
        # At expiration, spot = 110
        payoff = call.payoff_at_expiration(110)
        expected = 110 - 100 - 5.00  # intrinsic - premium
        assert payoff == pytest.approx(expected)
        assert payoff > 0
    
    def test_long_call_payoff_otm(self):
        """Long call should have negative payoff (max loss) when OTM."""
        call = create_long_call(strike=100, premium=5.00)
        
        # At expiration, spot = 90
        payoff = call.payoff_at_expiration(90)
        assert payoff == pytest.approx(-5.00)  # Just lose premium
    
    def test_long_call_payoff_atm(self):
        """Long call at ATM should have loss equal to premium."""
        call = create_long_call(strike=100, premium=5.00)
        
        payoff = call.payoff_at_expiration(100)
        assert payoff == pytest.approx(-5.00)
    
    def test_long_call_breakeven(self):
        """Long call breakeven should be strike + premium."""
        call = create_long_call(strike=100, premium=5.00)
        
        payoff = call.payoff_at_expiration(105)
        assert payoff == pytest.approx(0.0)
    
    def test_short_call_payoff(self):
        """Short call payoff should be inverse of long call."""
        long_call = create_long_call(strike=100, premium=5.00)
        short_call = create_short_call(strike=100, premium=5.00)
        
        for spot in [90, 95, 100, 105, 110]:
            assert long_call.payoff_at_expiration(spot) == pytest.approx(
                -short_call.payoff_at_expiration(spot)
            )
    
    def test_long_put_payoff_itm(self):
        """Long put should have positive payoff when ITM."""
        put = create_long_put(strike=100, premium=5.00)
        
        payoff = put.payoff_at_expiration(90)
        expected = 100 - 90 - 5.00
        assert payoff == pytest.approx(expected)
        assert payoff > 0
    
    def test_long_put_payoff_otm(self):
        """Long put should have negative payoff when OTM."""
        put = create_long_put(strike=100, premium=5.00)
        
        payoff = put.payoff_at_expiration(110)
        assert payoff == pytest.approx(-5.00)
    
    def test_short_put_payoff(self):
        """Short put payoff should be inverse of long put."""
        long_put = create_long_put(strike=100, premium=5.00)
        short_put = create_short_put(strike=100, premium=5.00)
        
        for spot in [90, 95, 100, 105, 110]:
            assert long_put.payoff_at_expiration(spot) == pytest.approx(
                -short_put.payoff_at_expiration(spot)
            )
    
    def test_vectorized_payoff(self):
        """Payoff calculation should work with numpy arrays."""
        call = create_long_call(strike=100, premium=5.00)
        
        spots = np.array([90, 95, 100, 105, 110])
        payoffs = call.payoff_at_expiration(spots)
        
        assert len(payoffs) == len(spots)
        assert payoffs[2] == pytest.approx(-5.00)  # ATM
        assert payoffs[4] == pytest.approx(5.00)   # $10 ITM
    
    def test_max_profit_long_call(self):
        """Long call should have unlimited max profit."""
        call = create_long_call(strike=100, premium=5.00)
        assert call.max_profit() is None
    
    def test_max_loss_long_call(self):
        """Long call max loss should be premium paid."""
        call = create_long_call(strike=100, premium=5.00, quantity=2)
        assert call.max_loss() == pytest.approx(10.00)
    
    def test_max_profit_short_call(self):
        """Short call max profit should be premium received."""
        call = create_short_call(strike=100, premium=5.00, quantity=3)
        assert call.max_profit() == pytest.approx(15.00)
    
    def test_max_loss_short_call(self):
        """Short call should have unlimited max loss."""
        call = create_short_call(strike=100, premium=5.00)
        assert call.max_loss() is None
    
    def test_invalid_strike(self):
        """Should raise error for negative strike."""
        with pytest.raises(ValueError, match="Strike price must be positive"):
            OptionPosition(strike=-100, premium=5.00)
    
    def test_invalid_premium(self):
        """Should raise error for negative premium."""
        with pytest.raises(ValueError, match="Premium cannot be negative"):
            OptionPosition(strike=100, premium=-5.00)
    
    def test_invalid_quantity(self):
        """Should raise error for zero quantity."""
        with pytest.raises(ValueError, match="Quantity cannot be zero"):
            OptionPosition(strike=100, premium=5.00, quantity=0)


class TestStrategy:
    """Tests for Strategy class."""
    
    def test_empty_strategy(self):
        """Empty strategy should have zero payoff."""
        strategy = Strategy("Empty")
        assert strategy.total_payoff(100) == 0
        assert strategy.total_payoff(np.array([90, 100, 110])).tolist() == [0, 0, 0]
    
    def test_single_leg_strategy(self):
        """Single leg strategy should match single option payoff."""
        call = create_long_call(strike=100, premium=5.00)
        
        strategy = Strategy("Single Call")
        strategy.add_position(call)
        
        for spot in [90, 100, 110]:
            assert strategy.total_payoff(spot) == call.payoff_at_expiration(spot)
    
    def test_multi_leg_strategy(self):
        """Multi-leg strategy should sum individual payoffs."""
        call = create_long_call(strike=100, premium=5.00)
        put = create_long_put(strike=100, premium=4.00)
        
        strategy = Strategy("Straddle")
        strategy.add_position(call).add_position(put)
        
        for spot in [90, 100, 110]:
            expected = call.payoff_at_expiration(spot) + put.payoff_at_expiration(spot)
            assert strategy.total_payoff(spot) == pytest.approx(expected)
    
    def test_payoff_matrix(self):
        """Payoff matrix should have correct structure."""
        strategy = create_long_straddle(strike=100, premium_call=3.00, premium_put=2.50)
        matrix = strategy.payoff_matrix(90, 110, num_points=5)
        
        assert 'underlying_price' in matrix.columns
        assert 'total_payoff' in matrix.columns
        assert len(matrix) == 5
    
    def test_net_premium(self):
        """Net premium calculation should be correct."""
        strategy = create_long_straddle(strike=100, premium_call=3.00, premium_put=2.50)
        
        # Long straddle: pay 3.00 + 2.50 = 5.50
        assert strategy.net_premium() == pytest.approx(-5.50)
    
    def test_to_dict(self):
        """Strategy serialization should work."""
        strategy = create_long_straddle(strike=100, premium_call=3.00, premium_put=2.50)
        data = strategy.to_dict()
        
        assert data['name'] == "Long Straddle"
        assert 'positions' in data
        assert len(data['positions']) == 2
        assert 'net_premium' in data


class TestPredefinedStrategies:
    """Tests for predefined strategy constructors."""
    
    def test_long_straddle(self):
        """Long straddle should have two long legs at same strike."""
        straddle = create_long_straddle(strike=100, premium_call=3.00, premium_put=2.50)
        
        assert straddle.name == "Long Straddle"
        assert len(straddle.positions) == 2
        
        # Both legs should be long
        for pos in straddle.positions:
            assert pos.side == OptionSide.LONG
        
        # One call, one put
        types = [pos.option_type for pos in straddle.positions]
        assert OptionType.CALL in types
        assert OptionType.PUT in types
        
        # Same strike
        assert straddle.positions[0].strike == straddle.positions[1].strike
    
    def test_short_straddle(self):
        """Short straddle should have two short legs."""
        straddle = create_short_straddle(strike=100, premium_call=3.00, premium_put=2.50)
        
        assert straddle.name == "Short Straddle"
        for pos in straddle.positions:
            assert pos.side == OptionSide.SHORT
    
    def test_long_strangle(self):
        """Long strangle should have OTM put and call at different strikes."""
        strangle = create_long_strangle(
            strike_low=95, strike_high=105,
            premium_put=1.50, premium_call=1.50
        )
        
        assert strangle.name == "Long Strangle"
        assert len(strangle.positions) == 2
        
        strikes = [pos.strike for pos in strangle.positions]
        assert 95 in strikes
        assert 105 in strikes
    
    def test_bull_call_spread(self):
        """Bull call spread should be long low strike, short high strike."""
        spread = create_bull_call_spread(
            strike_low=95, strike_high=105,
            premium_low=5.00, premium_high=2.00
        )
        
        assert spread.name == "Bull Call Spread"
        assert len(spread.positions) == 2
        
        # Find legs
        long_leg = [p for p in spread.positions if p.side == OptionSide.LONG][0]
        short_leg = [p for p in spread.positions if p.side == OptionSide.SHORT][0]
        
        assert long_leg.strike < short_leg.strike
        assert long_leg.option_type == OptionType.CALL
        assert short_leg.option_type == OptionType.CALL
    
    def test_bear_put_spread(self):
        """Bear put spread should be long high strike, short low strike."""
        spread = create_bear_put_spread(
            strike_low=95, strike_high=105,
            premium_low=1.50, premium_high=4.50
        )
        
        assert spread.name == "Bear Put Spread"
        
        long_leg = [p for p in spread.positions if p.side == OptionSide.LONG][0]
        short_leg = [p for p in spread.positions if p.side == OptionSide.SHORT][0]
        
        assert long_leg.strike > short_leg.strike
        assert long_leg.option_type == OptionType.PUT
    
    def test_long_butterfly(self):
        """Long butterfly should have three legs."""
        butterfly = create_long_butterfly(
            center_strike=100, wing_width=10,
            premium_low=1.00, premium_mid=3.00, premium_high=1.00
        )
        
        assert butterfly.name == "Long Butterfly"
        assert len(butterfly.positions) == 3
    
    def test_iron_condor(self):
        """Iron condor should have four legs."""
        condor = create_iron_condor(
            strike_put_low=90, strike_put_high=95,
            strike_call_low=105, strike_call_high=110,
            premium_put_low=0.50, premium_put_high=2.00,
            premium_call_low=2.00, premium_call_high=0.50
        )
        
        assert condor.name == "Iron Condor"
        assert len(condor.positions) == 4


class TestBreakevenAndMaxValues:
    """Tests for breakeven and max profit/loss calculations."""
    
    def test_long_straddle_breakevens(self):
        """Long straddle should have two breakeven points."""
        straddle = create_long_straddle(strike=100, premium_call=3.00, premium_put=2.50)
        
        breakevens = straddle.calculate_breakevens(80, 120)
        assert len(breakevens) == 2
        
        # Verify breakevens (approx strike +/- total premium)
        total_premium = 3.00 + 2.50
        assert abs(breakevens[0] - (100 - total_premium)) < 1
        assert abs(breakevens[1] - (100 + total_premium)) < 1
    
    def test_long_call_breakeven(self):
        """Long call should have one breakeven at strike + premium."""
        strategy = Strategy("Long Call")
        strategy.add_position(create_long_call(strike=100, premium=5.00))
        
        breakevens = strategy.calculate_breakevens(80, 120)
        assert len(breakevens) == 1
        assert breakevens[0] == pytest.approx(105.0)
    
    def test_long_straddle_max_loss(self):
        """Long straddle max loss should be total premium paid."""
        straddle = create_long_straddle(strike=100, premium_call=3.00, premium_put=2.50)
        
        max_profit, max_loss = straddle.max_profit_loss(80, 120)
        assert max_profit is None  # Unlimited
        assert max_loss == pytest.approx(5.50, abs=0.05)  # Allow sampling error
    
    def test_bull_call_spread_limited_risk_reward(self):
        """Bull call spread should have limited risk and reward."""
        spread = create_bull_call_spread(
            strike_low=95, strike_high=105,
            premium_low=5.00, premium_high=2.00
        )
        
        max_profit, max_loss = spread.max_profit_loss(80, 120)
        
        assert max_profit is not None
        assert max_loss is not None
        assert max_profit > 0
        assert max_loss > 0
