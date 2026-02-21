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

# Options analysis imports
from src.options import (
    create_long_call, create_long_put,
    create_long_straddle, create_short_straddle,
    create_long_strangle, create_short_strangle,
    create_bull_call_spread, create_bear_put_spread,
    create_long_butterfly, create_iron_condor,
    GreeksCalculator, PayoffPlotter, StrategyPlotter
)


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


def run_options_analysis(args):
    """Run options payoff and Greeks analysis."""
    print("\n" + "="*60)
    print("ALGORITHMIC TRADING SYSTEM - OPTIONS ANALYSIS")
    print("="*60 + "\n")
    
    logger = get_logger()
    logger.info(f"Starting options analysis for {args.option_strategy}")
    
    # Build the option strategy
    strategy_map = {
        'long-call': lambda: create_long_call(
            strike=args.strike or 100,
            premium=args.premium_call or 5.00
        ),
        'long-put': lambda: create_long_put(
            strike=args.strike or 100,
            premium=args.premium_put or 5.00
        ),
        'long-straddle': lambda: create_long_straddle(
            strike=args.strike or 100,
            premium_call=args.premium_call or 3.00,
            premium_put=args.premium_put or 2.50
        ),
        'short-straddle': lambda: create_short_straddle(
            strike=args.strike or 100,
            premium_call=args.premium_call or 3.00,
            premium_put=args.premium_put or 2.50
        ),
        'long-strangle': lambda: create_long_strangle(
            strike_low=args.strike_low or 95,
            strike_high=args.strike_high or 105,
            premium_put=args.premium_put or 1.50,
            premium_call=args.premium_call or 1.50
        ),
        'short-strangle': lambda: create_short_strangle(
            strike_low=args.strike_low or 95,
            strike_high=args.strike_high or 105,
            premium_put=args.premium_put or 1.50,
            premium_call=args.premium_call or 1.50
        ),
        'bull-call-spread': lambda: create_bull_call_spread(
            strike_low=args.strike_low or 95,
            strike_high=args.strike_high or 105,
            premium_low=args.premium_low or 5.00,
            premium_high=args.premium_high or 2.00
        ),
        'bear-put-spread': lambda: create_bear_put_spread(
            strike_low=args.strike_low or 95,
            strike_high=args.strike_high or 105,
            premium_low=args.premium_low or 1.50,
            premium_high=args.premium_high or 4.50
        ),
        'long-butterfly': lambda: create_long_butterfly(
            center_strike=args.strike or 100,
            wing_width=args.wing_width or 10,
            premium_low=args.premium_low or 1.00,
            premium_mid=args.premium_mid or 3.00,
            premium_high=args.premium_high or 1.00
        ),
        'iron-condor': lambda: create_iron_condor(
            strike_put_low=args.strike_low or 90,
            strike_put_high=args.strike or 95,
            strike_call_low=args.strike or 105,
            strike_call_high=args.strike_high or 110,
            premium_put_low=args.premium_put_low or 0.50,
            premium_put_high=args.premium_put or 2.00,
            premium_call_low=args.premium_call or 2.00,
            premium_call_high=args.premium_call_high or 0.50
        )
    }
    
    strategy_builder = strategy_map.get(args.option_strategy)
    if not strategy_builder:
        print(f"Error: Unknown option strategy '{args.option_strategy}'")
        print(f"Available strategies: {', '.join(strategy_map.keys())}")
        sys.exit(1)
    
    strategy = strategy_builder()
    
    print(f"Strategy: {strategy.name}")
    print(f"Number of legs: {len(strategy.positions)}")
    print(f"Net Premium: ${strategy.net_premium():+.2f}\n")
    
    # Calculate payoff metrics
    min_price = args.min_price or (args.strike or 100) * 0.8
    max_price = args.max_price or (args.strike or 100) * 1.2
    
    breakevens = strategy.calculate_breakevens(min_price, max_price)
    max_profit, max_loss = strategy.max_profit_loss(min_price, max_price)
    
    print("Payoff Analysis:")
    print(f"  Breakeven Points: {', '.join(f'${b:.2f}' for b in breakevens) if breakevens else 'None'}")
    print(f"  Max Profit: {'Unlimited' if max_profit is None else f'${max_profit:.2f}'}")
    print(f"  Max Loss: {'Unlimited' if max_loss is None else f'${max_loss:.2f}'}")
    
    # Greeks analysis
    if args.calc_greeks:
        print("\nGreeks Analysis:")
        calc = GreeksCalculator(risk_free_rate=args.risk_free_rate, volatility=args.volatility)
        
        spot = args.spot or (args.strike or 100)
        time_to_expiry = args.days_to_expiry / 365.0
        
        from src.options.greeks import StrategyGreeks
        strategy_greeks = StrategyGreeks(strategy)
        agg = strategy_greeks.calculate(
            spot=spot,
            time_to_expiry=time_to_expiry,
            volatility=args.volatility,
            risk_free_rate=args.risk_free_rate
        )
        
        print(f"  Current Spot: ${spot:.2f}")
        print(f"  Time to Expiry: {args.days_to_expiry} days")
        print(f"  Volatility: {args.volatility:.1%}")
        print(f"  Risk-Free Rate: {args.risk_free_rate:.1%}")
        print(f"\n  Aggregated Greeks:")
        print(f"    Delta:  {agg.delta:+.4f}")
        print(f"    Gamma:  {agg.gamma:.4f}")
        print(f"    Theta:  {agg.theta/365:.4f} (daily)")
        print(f"    Vega:   {agg.vega:.4f}")
        print(f"    Rho:    {agg.rho:.4f}")
    
    # Generate plots
    if args.plot:
        print("\nGenerating plots...")
        output_file = args.output or f"options_{args.option_strategy}.html"
        
        plotter = StrategyPlotter(use_plotly=True)
        spot = args.spot or (args.strike or 100)
        
        fig = plotter.plot_strategy_analysis(
            strategy=strategy,
            spot=spot,
            min_price=min_price,
            max_price=max_price,
            time_to_expiry=args.days_to_expiry / 365.0,
            volatility=args.volatility,
            risk_free_rate=args.risk_free_rate,
            show=False,
            save_path=output_file
        )
        print(f"  ✓ Analysis saved to: {output_file}")
    
    # Payoff matrix output
    if args.show_matrix:
        print("\nPayoff Matrix (sample):")
        matrix = strategy.payoff_matrix(min_price, max_price, num_points=10)
        print(matrix[['underlying_price', 'total_payoff']].to_string(index=False))
    
    logger.info("Options analysis completed")
    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description='Algorithmic Trading System with Backtesting and Paper Trading'
    )
    
    parser.add_argument(
        '--mode',
        choices=['backtest', 'paper', 'options'],
        default='backtest',
        help='Trading mode: backtest, paper trading, or options analysis'
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
    
    # Options analysis arguments
    parser.add_argument(
        '--option-strategy',
        choices=['long-call', 'long-put', 'long-straddle', 'short-straddle',
                 'long-strangle', 'short-strangle', 'bull-call-spread',
                 'bear-put-spread', 'long-butterfly', 'iron-condor'],
        help='Options strategy type (for options mode)'
    )
    
    parser.add_argument(
        '--strike',
        type=float,
        help='Strike price (or center strike for symmetric strategies)'
    )
    
    parser.add_argument(
        '--strike-low',
        type=float,
        help='Lower strike price (for spreads, strangles)'
    )
    
    parser.add_argument(
        '--strike-high',
        type=float,
        help='Higher strike price (for spreads, strangles)'
    )
    
    parser.add_argument(
        '--premium-call',
        type=float,
        help='Call option premium'
    )
    
    parser.add_argument(
        '--premium-put',
        type=float,
        help='Put option premium'
    )
    
    parser.add_argument(
        '--premium-low',
        type=float,
        help='Premium for lower strike option (spreads)'
    )
    
    parser.add_argument(
        '--premium-high',
        type=float,
        help='Premium for higher strike option (spreads)'
    )
    
    parser.add_argument(
        '--premium-mid',
        type=float,
        help='Premium for center strike option (butterfly)'
    )
    
    parser.add_argument(
        '--premium-put-low',
        type=float,
        help='Premium for lower strike put (iron condor)'
    )
    
    parser.add_argument(
        '--premium-call-high',
        type=float,
        help='Premium for higher strike call (iron condor)'
    )
    
    parser.add_argument(
        '--wing-width',
        type=float,
        help='Wing width for butterfly spread'
    )
    
    parser.add_argument(
        '--spot',
        type=float,
        help='Current underlying price'
    )
    
    parser.add_argument(
        '--min-price',
        type=float,
        help='Minimum price for payoff analysis'
    )
    
    parser.add_argument(
        '--max-price',
        type=float,
        help='Maximum price for payoff analysis'
    )
    
    parser.add_argument(
        '--days-to-expiry',
        type=int,
        default=30,
        help='Days to expiration (for Greeks calculation)'
    )
    
    parser.add_argument(
        '--volatility',
        type=float,
        default=0.20,
        help='Annualized volatility (for Greeks calculation)'
    )
    
    parser.add_argument(
        '--risk-free-rate',
        type=float,
        default=0.05,
        help='Annual risk-free interest rate'
    )
    
    parser.add_argument(
        '--calc-greeks',
        action='store_true',
        help='Calculate Greeks (options mode)'
    )
    
    parser.add_argument(
        '--show-matrix',
        action='store_true',
        help='Show payoff matrix (options mode)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path for plots (options mode)'
    )
    
    args = parser.parse_args()
    
    Config.ensure_dirs()
    
    if args.mode == 'backtest':
        run_backtest(args)
    elif args.mode == 'paper':
        run_paper_trading(args)
    elif args.mode == 'options':
        if not args.option_strategy:
            print("Error: --option-strategy is required for options mode")
            sys.exit(1)
        run_options_analysis(args)


if __name__ == '__main__':
    main()
