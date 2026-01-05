import pytest
from src.risk.portfolio import Portfolio
from src.risk.risk_manager import RiskManager


@pytest.fixture
def portfolio():
    return Portfolio(initial_capital=100000)


@pytest.fixture
def risk_manager(portfolio):
    return RiskManager(portfolio, max_position_size=0.10, max_drawdown=0.20)


def test_risk_manager_initialization(risk_manager):
    assert risk_manager.max_position_size == 0.10
    assert risk_manager.max_drawdown == 0.20


def test_check_buy_order_sufficient_cash(risk_manager):
    can_trade, reason = risk_manager.check_trade('TEST', 100, 50.0, 'BUY')
    
    assert can_trade is True


def test_check_buy_order_insufficient_cash(risk_manager):
    can_trade, reason = risk_manager.check_trade('TEST', 10000, 50.0, 'BUY')
    
    assert can_trade is False
    assert 'Insufficient cash' in reason


def test_check_buy_order_exceeds_position_size(risk_manager):
    can_trade, reason = risk_manager.check_trade('TEST', 500, 50.0, 'BUY')
    
    assert can_trade is False
    assert 'Position size' in reason


def test_check_sell_order_no_position(risk_manager):
    can_trade, reason = risk_manager.check_trade('TEST', 100, 50.0, 'SELL')
    
    assert can_trade is False
    assert 'No position' in reason


def test_check_sell_order_with_position(risk_manager):
    risk_manager.portfolio.update_position('TEST', 100, 50.0, 'BUY')
    
    can_trade, reason = risk_manager.check_trade('TEST', 50, 55.0, 'SELL')
    
    assert can_trade is True


def test_calculate_position_size(risk_manager):
    shares = risk_manager.calculate_position_size(price=100.0, stop_loss_pct=0.02)
    
    assert shares > 0
    assert shares * 100 <= risk_manager.portfolio.portfolio_value * risk_manager.max_position_size


def test_should_stop_trading_normal(risk_manager):
    should_stop, reason = risk_manager.should_stop_trading()
    
    assert should_stop is False


def test_should_stop_trading_max_drawdown(risk_manager):
    risk_manager.portfolio.peak_value = 100000
    risk_manager.portfolio.portfolio_value = 75000
    
    should_stop, reason = risk_manager.should_stop_trading()
    
    assert should_stop is True
    assert 'drawdown' in reason.lower()
