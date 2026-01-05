#!/usr/bin/env python3
"""
Simple example demonstrating a backtest using the algorithmic trading system.
"""

from datetime import datetime, timedelta
from src.data.data_fetcher import DataFetcher
from src.strategy.example_strategies import SMAcrossoverStrategy
from src.backtesting.backtest_engine import BacktestEngine
from src.config import Config

def main():
    print("\n" + "="*60)
    print("ALGORITHMIC TRADING SYSTEM - SIMPLE BACKTEST EXAMPLE")
    print("="*60 + "\n")
    
    Config.ensure_dirs()
    
    symbol = 'SPY'
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Fetching {symbol} data from {start_date} to {end_date}...")
    
    data_fetcher = DataFetcher()
    try:
        data = data_fetcher.fetch_historical_data(symbol, start_date, end_date)
        print(f"✓ Fetched {len(data)} bars of data\n")
    except Exception as e:
        print(f"✗ Error fetching data: {str(e)}")
        return
    
    print("Initializing SMA Crossover Strategy (20/50)...")
    strategy = SMAcrossoverStrategy(short_window=20, long_window=50)
    
    print("Setting up backtest engine...")
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=100000,
        commission=0.0,
        slippage=0.001
    )
    
    engine.load_data(symbol, data)
    
    print("Running backtest...\n")
    results = engine.run([symbol])
    
    engine.print_results()
    
    print("\nBacktest completed successfully!")
    print(f"Check the logs directory for detailed logs.")

if __name__ == '__main__':
    main()
