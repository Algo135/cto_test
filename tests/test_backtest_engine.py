import pytest
import pandas as pd
import numpy as np
from src.backtesting.backtest_engine import BacktestEngine
from src.strategy.example_strategies import SMAcrossoverStrategy


@pytest.fixture
def sample_data():
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    close_prices = 100 + np.random.randn(100).cumsum()
    
    data = pd.DataFrame({
        'open': close_prices * (1 + np.random.randn(100) * 0.01),
        'high': close_prices * (1 + abs(np.random.randn(100) * 0.02)),
        'low': close_prices * (1 - abs(np.random.randn(100) * 0.02)),
        'close': close_prices,
        'volume': np.random.randint(1000000, 10000000, 100)
    }, index=dates)
    
    data['high'] = data[['open', 'high', 'close']].max(axis=1)
    data['low'] = data[['open', 'low', 'close']].min(axis=1)
    
    return data


def test_backtest_engine_initialization():
    strategy = SMAcrossoverStrategy(20, 50)
    engine = BacktestEngine(strategy, initial_capital=100000)
    
    assert engine.initial_capital == 100000
    assert engine.strategy == strategy
    assert engine.portfolio.initial_capital == 100000


def test_backtest_engine_load_data(sample_data):
    strategy = SMAcrossoverStrategy(10, 20)
    engine = BacktestEngine(strategy)
    
    engine.load_data('TEST', sample_data)
    
    assert 'TEST' in engine.data
    assert len(engine.data['TEST']) == len(sample_data)


def test_backtest_engine_run(sample_data):
    strategy = SMAcrossoverStrategy(10, 20)
    engine = BacktestEngine(strategy, initial_capital=100000)
    
    engine.load_data('TEST', sample_data)
    results = engine.run(['TEST'])
    
    assert 'total_return' in results
    assert 'sharpe_ratio' in results
    assert 'max_drawdown' in results
    assert 'total_trades' in results
    assert 'win_rate' in results


def test_backtest_multiple_symbols(sample_data):
    strategy = SMAcrossoverStrategy(10, 20)
    engine = BacktestEngine(strategy, initial_capital=100000)
    
    engine.load_data('TEST1', sample_data)
    engine.load_data('TEST2', sample_data)
    
    results = engine.run(['TEST1', 'TEST2'])
    
    assert results is not None
    assert 'total_return' in results


def test_backtest_with_commission(sample_data):
    strategy = SMAcrossoverStrategy(10, 20)
    engine = BacktestEngine(strategy, initial_capital=100000, commission=5.0)
    
    engine.load_data('TEST', sample_data)
    results = engine.run(['TEST'])
    
    assert engine.commission == 5.0
