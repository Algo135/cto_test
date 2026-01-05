#!/usr/bin/env python3

import argparse
import sys
from datetime import datetime, timedelta

from src.data.data_fetcher import DataFetcher
from src.data.data_store import DataStore
from src.strategy.example_strategies import (
    SMAcrossoverStrategy,
    RSIStrategy,
    BollingerBandsStrategy,
    MACDStrategy
)
from src.backtesting.backtest_engine import BacktestEngine
from src.backtesting.performance import PerformanceAnalyzer
from src.paper_trading.paper_trader import PaperTrader
from src.config import Config
from src.monitoring.logger import get_logger


def run_backtest(args):
    print("\n" + "="*60)
    print("ALGORITHMIC TRADING SYSTEM - BACKTEST MODE")
    print("="*60 + "\n")
    
    logger = get_logger()
    logger.info("Starting backtest")
    
    strategy_map = {
        'sma': SMAcrossoverStrategy(args.sma_short, args.sma_long),
        'rsi': RSIStrategy(args.rsi_period, args.rsi_oversold, args.rsi_overbought),
        'bollinger': BollingerBandsStrategy(args.bb_period, args.bb_std),
        'macd': MACDStrategy(args.macd_fast, args.macd_slow, args.macd_signal)
    }
    
    strategy = strategy_map.get(args.strategy)
    if not strategy:
        print(f"Error: Unknown strategy '{args.strategy}'")
        sys.exit(1)
    
    print(f"Strategy: {strategy.name}")
    print(f"Symbols: {', '.join(args.symbols)}")
    print(f"Period: {args.start} to {args.end}")
    print(f"Initial Capital: ${args.capital:,.2f}\n")
    
    data_fetcher = DataFetcher()
    data_store = DataStore()
    
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=args.capital,
        commission=args.commission,
        slippage=args.slippage
    )
    
    for symbol in args.symbols:
        print(f"Fetching data for {symbol}...")
        try:
            data = data_fetcher.fetch_historical_data(symbol, args.start, args.end)
            engine.load_data(symbol, data)
            
            if not data_store.has_data(symbol):
                data_store.save_data(symbol, data)
            
            print(f"  ✓ Loaded {len(data)} bars for {symbol}")
        except Exception as e:
            print(f"  ✗ Failed to fetch {symbol}: {str(e)}")
            sys.exit(1)
    
    print("\nRunning backtest...")
    results = engine.run(args.symbols)
    
    engine.print_results()
    
    if args.plot:
        print("Generating performance plots...")
        analyzer = PerformanceAnalyzer(results)
        analyzer.plot_equity_curve(show=False, save_path='backtest_equity_curve.html')
        analyzer.plot_drawdown(show=False, save_path='backtest_drawdown.html')
        analyzer.plot_returns_distribution(show=False, save_path='backtest_returns.html')
        print("  ✓ Plots saved to current directory")
    
    logger.info("Backtest completed")


def run_paper_trading(args):
    print("\n" + "="*60)
    print("ALGORITHMIC TRADING SYSTEM - PAPER TRADING MODE")
    print("="*60 + "\n")
    
    logger = get_logger()
    logger.info("Starting paper trading")
    
    strategy_map = {
        'sma': SMAcrossoverStrategy(args.sma_short, args.sma_long),
        'rsi': RSIStrategy(args.rsi_period, args.rsi_oversold, args.rsi_overbought),
        'bollinger': BollingerBandsStrategy(args.bb_period, args.bb_std),
        'macd': MACDStrategy(args.macd_fast, args.macd_slow, args.macd_signal)
    }
    
    strategy = strategy_map.get(args.strategy)
    if not strategy:
        print(f"Error: Unknown strategy '{args.strategy}'")
        sys.exit(1)
    
    print(f"Strategy: {strategy.name}")
    print(f"Symbols: {', '.join(args.symbols)}")
    print(f"Poll Interval: {args.interval} seconds")
    print(f"Use Alpaca: {args.use_alpaca}\n")
    
    trader = PaperTrader(
        strategy=strategy,
        symbols=args.symbols,
        use_alpaca=args.use_alpaca,
        initial_capital=args.capital
    )
    
    trader.start(poll_interval=args.interval)


def main():
    parser = argparse.ArgumentParser(
        description='Algorithmic Trading System with Backtesting and Paper Trading'
    )
    
    parser.add_argument(
        '--mode',
        choices=['backtest', 'paper'],
        default='backtest',
        help='Trading mode: backtest or paper trading'
    )
    
    parser.add_argument(
        '--symbols',
        nargs='+',
        default=['SPY'],
        help='Stock symbols to trade (space-separated)'
    )
    
    parser.add_argument(
        '--strategy',
        choices=['sma', 'rsi', 'bollinger', 'macd'],
        default='sma',
        help='Trading strategy to use'
    )
    
    parser.add_argument(
        '--capital',
        type=float,
        default=100000,
        help='Initial capital'
    )
    
    parser.add_argument(
        '--start',
        default=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
        help='Backtest start date (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end',
        default=datetime.now().strftime('%Y-%m-%d'),
        help='Backtest end date (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--commission',
        type=float,
        default=0.0,
        help='Commission per trade'
    )
    
    parser.add_argument(
        '--slippage',
        type=float,
        default=0.001,
        help='Slippage percentage (e.g., 0.001 for 0.1%)'
    )
    
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Generate performance plots (backtest only)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Poll interval in seconds (paper trading only)'
    )
    
    parser.add_argument(
        '--use-alpaca',
        action='store_true',
        help='Use Alpaca API for paper trading (requires API keys)'
    )
    
    parser.add_argument(
        '--sma-short',
        type=int,
        default=20,
        help='SMA strategy: short window'
    )
    
    parser.add_argument(
        '--sma-long',
        type=int,
        default=50,
        help='SMA strategy: long window'
    )
    
    parser.add_argument(
        '--rsi-period',
        type=int,
        default=14,
        help='RSI strategy: period'
    )
    
    parser.add_argument(
        '--rsi-oversold',
        type=int,
        default=30,
        help='RSI strategy: oversold threshold'
    )
    
    parser.add_argument(
        '--rsi-overbought',
        type=int,
        default=70,
        help='RSI strategy: overbought threshold'
    )
    
    parser.add_argument(
        '--bb-period',
        type=int,
        default=20,
        help='Bollinger Bands strategy: period'
    )
    
    parser.add_argument(
        '--bb-std',
        type=float,
        default=2.0,
        help='Bollinger Bands strategy: standard deviations'
    )
    
    parser.add_argument(
        '--macd-fast',
        type=int,
        default=12,
        help='MACD strategy: fast period'
    )
    
    parser.add_argument(
        '--macd-slow',
        type=int,
        default=26,
        help='MACD strategy: slow period'
    )
    
    parser.add_argument(
        '--macd-signal',
        type=int,
        default=9,
        help='MACD strategy: signal period'
    )
    
    args = parser.parse_args()
    
    Config.ensure_dirs()
    
    if args.mode == 'backtest':
        run_backtest(args)
    elif args.mode == 'paper':
        run_paper_trading(args)


if __name__ == '__main__':
    main()
