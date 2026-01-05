import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.strategy.example_strategies import (
    SMAcrossoverStrategy,
    RSIStrategy,
    BollingerBandsStrategy,
    MACDStrategy
)
from src.strategy.base_strategy import Signal


@pytest.fixture
def sample_data():
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    data = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000000, 10000000, 100)
    }, index=dates)
    
    data['high'] = data[['open', 'high', 'close']].max(axis=1)
    data['low'] = data[['open', 'low', 'close']].min(axis=1)
    
    return data


def test_sma_crossover_strategy(sample_data):
    strategy = SMAcrossoverStrategy(short_window=10, long_window=20)
    signals = strategy.generate_signals('TEST', sample_data)
    
    assert isinstance(signals, list)
    for signal in signals:
        assert isinstance(signal, Signal)
        assert signal.signal_type in [Signal.BUY, Signal.SELL]


def test_rsi_strategy(sample_data):
    strategy = RSIStrategy(period=14, oversold=30, overbought=70)
    signals = strategy.generate_signals('TEST', sample_data)
    
    assert isinstance(signals, list)
    for signal in signals:
        assert isinstance(signal, Signal)


def test_bollinger_bands_strategy(sample_data):
    strategy = BollingerBandsStrategy(period=20, num_std=2.0)
    signals = strategy.generate_signals('TEST', sample_data)
    
    assert isinstance(signals, list)
    for signal in signals:
        assert isinstance(signal, Signal)


def test_macd_strategy(sample_data):
    strategy = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
    signals = strategy.generate_signals('TEST', sample_data)
    
    assert isinstance(signals, list)
    for signal in signals:
        assert isinstance(signal, Signal)


def test_strategy_on_bar():
    strategy = SMAcrossoverStrategy(short_window=5, long_window=10)
    
    for i in range(20):
        bar_event = type('BarEvent', (), {
            'symbol': 'TEST',
            'timestamp': datetime.now(),
            'open': 100 + i,
            'high': 102 + i,
            'low': 98 + i,
            'close': 100 + i,
            'volume': 1000000
        })()
        
        signal = strategy.on_bar(bar_event)
        
        if signal:
            assert isinstance(signal, Signal)
            assert signal.symbol == 'TEST'
