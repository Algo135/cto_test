"""Tests for options strategy constructors and behavior."""

import pytest
import numpy as np

from src.options.payoff import (
    Strategy, OptionPosition, OptionType, OptionSide,
    create_long_call, create_short_call, create_long_put, create_short_put,
    create_long_straddle, create_short_straddle,
    create_long_strangle, create_short_strangle,
    create_bull_call_spread, create_bear_put_spread,
    create_long_butterfly, create_iron_condor, create_collar
)


class TestStrategyConstruction:
    """Tests for strategy building and manipulation."""
    
    def test_empty_strategy_creation(self):
        """Empty strategy should initialize correctly."""
        strategy = Strategy("Test Strategy")
        assert strategy.name == "Test Strategy"
        assert len(strategy.positions) == 0
    
    def test_add_position(self):
        """Should be able to add positions."""
        strategy = Strategy()
        call = create_long_call(strike=100, premium=5.00)
        
        result = strategy.add_position(call)
        
        assert len(strategy.positions) == 1
        assert result is strategy  # For method chaining
    
    def test_remove_position(self):
        """Should be able to remove positions by index."""
        strategy = Strategy()
        strategy.add_position(create_long_call(100, 5.00))
        strategy.add_position(create_long_put(100, 4.00))
        
        strategy.remove_position(0)
        
        assert len(strategy.positions) == 1
        assert strategy.positions[0].option_type == OptionType.PUT
    
    def test_remove_invalid_index(self):
        """Removing invalid index should not raise error."""
        strategy = Strategy()
        strategy.add_position(create_long_call(100, 5.00))
        
        strategy.remove_position(5)  # Out of bounds
        strategy.remove_position(-1)  # Negative
        
        assert len(strategy.positions) == 1
    
    def test_chaining(self):
        """Method chaining should work."""
        strategy = Strategy("Chained")
        result = (strategy
                 .add_position(create_long_call(100, 5.00))
                 .add_position(create_long_put(100, 4.00))
                 .remove_position(0))
        
        assert result is strategy
        assert len(strategy.positions) == 1


class TestStraddleVariations:
    """Tests for straddle strategies."""
    
    def test_long_straddle_payoff_symmetry(self):
        """Long straddle should have symmetric payoff around strike."""
        straddle = create_long_straddle(strike=100, premium_call=3.00, premium_put=2.50)
        
        # Payoffs at equal distances from strike should be equal
        payoff_95 = straddle.total_payoff(95)
        payoff_105 = straddle.total_payoff(105)
        
        assert payoff_95 == pytest.approx(payoff_105)
    
    def test_long_straddle_minimum_payoff(self):
        """Long straddle minimum payoff should be at strike."""
        straddle = create_long_straddle(strike=100, premium_call=3.00, premium_put=2.50)
        
        prices = np.linspace(80, 120, 100)
        payoffs = straddle.total_payoff(prices)
        
        min_idx = np.argmin(payoffs)
        min_price = prices[min_idx]
        
        assert abs(min_price - 100) < 1  # Minimum near strike
    
    def test_short_straddle_inverse(self):
        """Short straddle payoff should be inverse of long straddle."""
        long_straddle = create_long_straddle(100, 3.00, 2.50)
        short_straddle = create_short_straddle(100, 3.00, 2.50)
        
        for price in [90, 95, 100, 105, 110]:
            assert long_straddle.total_payoff(price) == pytest.approx(
                -short_straddle.total_payoff(price)
            )
    
    def test_straddle_quantity_scaling(self):
        """Straddle with quantity should scale payoffs."""
        straddle_1x = create_long_straddle(100, 3.00, 2.50, quantity=1)
        straddle_2x = create_long_straddle(100, 3.00, 2.50, quantity=2)
        
        for price in [90, 100, 110]:
            assert straddle_2x.total_payoff(price) == pytest.approx(
                2 * straddle_1x.total_payoff(price)
            )


class TestStrangleVariations:
    """Tests for strangle strategies."""
    
    def test_long_strangle_strike_order(self):
        """Long strangle should have put at low strike, call at high strike."""
        strangle = create_long_strangle(
            strike_low=95, strike_high=105,
            premium_put=1.50, premium_call=1.50
        )
        
        strikes = [pos.strike for pos in strangle.positions]
        assert min(strikes) == 95
        assert max(strikes) == 105
    
    def test_strangle_vs_straddle_cost(self):
        """Strangle should typically cost less than straddle."""
        straddle = create_long_straddle(100, 5.00, 4.00)
        strangle = create_long_strangle(95, 105, 2.00, 2.00)
        
        straddle_cost = abs(straddle.net_premium())
        strangle_cost = abs(strangle.net_premium())
        
        assert strangle_cost < straddle_cost
    
    def test_strangle_flat_region(self):
        """Strangle should have flat payoff region between strikes."""
        strangle = create_long_strangle(95, 105, 1.50, 1.50)
        
        # Between strikes, both options OTM
        payoff_98 = strangle.total_payoff(98)
        payoff_100 = strangle.total_payoff(100)
        payoff_102 = strangle.total_payoff(102)
        
        # All should equal max loss (total premium paid)
        assert payoff_98 == pytest.approx(payoff_100)
        assert payoff_100 == pytest.approx(payoff_102)


class TestSpreadStrategies:
    """Tests for spread strategies."""
    
    def test_bull_call_spread_debit(self):
        """Bull call spread is typically a debit spread."""
        spread = create_bull_call_spread(
            strike_low=95, strike_high=105,
            premium_low=5.00, premium_high=2.00
        )
        
        # Pay more for lower strike call, receive less for higher strike
        assert spread.net_premium() < 0  # Net debit
    
    def test_bull_call_spread_max_profit(self):
        """Bull call spread max profit should be width minus net debit."""
        spread = create_bull_call_spread(95, 105, 5.00, 2.00)
        
        width = 105 - 95
        net_debit = abs(spread.net_premium())
        expected_max = width - net_debit
        
        max_profit, _ = spread.max_profit_loss(80, 120)
        assert max_profit == pytest.approx(expected_max, abs=0.01)
    
    def test_bull_call_spread_max_loss(self):
        """Bull call spread max loss should be net debit."""
        spread = create_bull_call_spread(95, 105, 5.00, 2.00)
        
        _, max_loss = spread.max_profit_loss(80, 120)
        assert max_loss == pytest.approx(abs(spread.net_premium()), abs=0.01)
    
    def test_bear_put_spread_debit(self):
        """Bear put spread is typically a debit spread."""
        spread = create_bear_put_spread(
            strike_low=95, strike_high=105,
            premium_low=1.50, premium_high=4.50
        )
        
        assert spread.net_premium() < 0
    
    def test_spread_limited_risk(self):
        """Spreads should have limited risk and reward."""
        bull_spread = create_bull_call_spread(95, 105, 5.00, 2.00)
        bear_spread = create_bear_put_spread(95, 105, 1.50, 4.50)
        
        for spread in [bull_spread, bear_spread]:
            max_p, max_l = spread.max_profit_loss(80, 120)
            assert max_p is not None  # Limited profit
            assert max_l is not None  # Limited loss


class TestButterflyStrategy:
    """Tests for butterfly spread strategies."""
    
    def test_butterfly_structure(self):
        """Butterfly should have three legs."""
        butterfly = create_long_butterfly(
            center_strike=100, wing_width=10,
            premium_low=1.00, premium_mid=3.00, premium_high=1.00
        )
        
        assert len(butterfly.positions) == 3
    
    def test_butterfly_max_profit_at_center(self):
        """Butterfly max profit should be at center strike."""
        butterfly = create_long_butterfly(100, 10, 1.00, 3.00, 1.00)
        
        prices = np.linspace(80, 120, 100)
        payoffs = butterfly.total_payoff(prices)
        
        max_payoff = np.max(payoffs)
        max_idx = np.argmax(payoffs)
        max_price = prices[max_idx]
        
        assert abs(max_price - 100) < 2
        assert max_payoff > 0
    
    def test_butterfly_limited_risk(self):
        """Butterfly should have limited risk and reward."""
        butterfly = create_long_butterfly(100, 10, 1.00, 3.00, 1.00)
        
        max_p, max_l = butterfly.max_profit_loss(70, 130)
        
        assert max_p is not None
        assert max_l is not None
        assert max_p > 0
        assert max_l > 0


class TestIronCondor:
    """Tests for iron condor strategy."""
    
    def test_iron_condor_structure(self):
        """Iron condor should have four legs."""
        condor = create_iron_condor(
            strike_put_low=90, strike_put_high=95,
            strike_call_low=105, strike_call_high=110,
            premium_put_low=0.50, premium_put_high=2.00,
            premium_call_low=2.00, premium_call_high=0.50
        )
        
        assert len(condor.positions) == 4
        assert condor.name == "Iron Condor"
    
    def test_iron_condor_net_credit(self):
        """Iron condor is typically a net credit strategy."""
        condor = create_iron_condor(
            90, 95, 105, 110,
            0.50, 2.00, 2.00, 0.50
        )
        
        assert condor.net_premium() > 0  # Net credit
    
    def test_iron_condor_profit_region(self):
        """Iron condor should profit in region between inner strikes."""
        condor = create_iron_condor(
            90, 95, 105, 110,
            0.50, 2.00, 2.00, 0.50
        )
        
        # Should profit between 95 and 105
        payoff_100 = condor.total_payoff(100)
        assert payoff_100 > 0
        
        # Should lose outside wings
        payoff_85 = condor.total_payoff(85)
        payoff_115 = condor.total_payoff(115)
        assert payoff_85 < 0
        assert payoff_115 < 0
    
    def test_iron_condor_max_loss(self):
        """Iron condor max loss should be limited."""
        condor = create_iron_condor(
            90, 95, 105, 110,
            0.50, 2.00, 2.00, 0.50
        )
        
        max_p, max_l = condor.max_profit_loss(80, 120)
        
        assert max_p is not None
        assert max_l is not None
        assert max_l > 0


class TestCollar:
    """Tests for collar strategy."""
    
    def test_collar_structure(self):
        """Collar should have three legs (stock, put, call)."""
        collar = create_collar(
            stock_price=100,
            put_strike=95, call_strike=105,
            put_premium=2.00, call_premium=2.00
        )
        
        assert len(collar.positions) == 3
        assert collar.name == "Collar"


class TestBreakevenAccuracy:
    """Tests for breakeven calculation accuracy."""
    
    def test_call_breakeven_exact(self):
        """Call breakeven should be exactly strike + premium."""
        strategy = Strategy()
        strategy.add_position(create_long_call(100, 5.00))
        
        breakevens = strategy.calculate_breakevens(80, 120)
        assert len(breakevens) == 1
        assert breakevens[0] == pytest.approx(105.0, abs=0.1)
    
    def test_put_breakeven_exact(self):
        """Put breakeven should be exactly strike - premium."""
        strategy = Strategy()
        strategy.add_position(create_long_put(100, 5.00))
        
        breakevens = strategy.calculate_breakevens(80, 120)
        assert len(breakevens) == 1
        assert breakevens[0] == pytest.approx(95.0, abs=0.1)
    
    def test_spread_breakevens(self):
        """Spread should have at most one breakeven."""
        spread = create_bull_call_spread(95, 105, 5.00, 2.00)
        
        breakevens = spread.calculate_breakevens(80, 120)
        assert len(breakevens) <= 1


class TestStrategySerialization:
    """Tests for strategy serialization."""
    
    def test_strategy_to_dict(self):
        """Strategy should serialize to dictionary."""
        straddle = create_long_straddle(100, 3.00, 2.50)
        
        data = straddle.to_dict()
        
        assert 'name' in data
        assert 'positions' in data
        assert 'net_premium' in data
        assert len(data['positions']) == 2
    
    def test_position_to_dict(self):
        """Position should serialize to dictionary."""
        call = create_long_call(100, 5.00, quantity=2)
        
        data = call.to_dict()
        
        assert data['strike'] == 100
        assert data['premium'] == 5.00
        assert data['quantity'] == 2
        assert data['option_type'] == 'call'
        assert data['side'] == 'long'
