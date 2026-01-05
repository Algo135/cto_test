import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
from src.strategy.base_strategy import BaseStrategy, Signal
from src.risk.portfolio import Portfolio
from src.risk.risk_manager import RiskManager
from src.config import Config


class BacktestEngine:
    def __init__(
        self,
        strategy: BaseStrategy,
        initial_capital: float = None,
        commission: float = None,
        slippage: float = None
    ):
        self.strategy = strategy
        self.initial_capital = initial_capital or Config.INITIAL_CAPITAL
        self.commission = commission or Config.COMMISSION_PER_TRADE
        self.slippage = slippage or Config.SLIPPAGE_PERCENT
        
        self.portfolio = Portfolio(self.initial_capital)
        self.risk_manager = RiskManager(self.portfolio)
        
        self.data = {}
        self.current_prices = {}
        self.results = {}
    
    def load_data(self, symbol: str, data: pd.DataFrame):
        self.data[symbol] = data
    
    def run(self, symbols: List[str] = None) -> dict:
        if symbols is None:
            symbols = list(self.data.keys())
        
        if not symbols:
            raise ValueError("No symbols to backtest")
        
        all_dates = sorted(set().union(*[set(self.data[s].index) for s in symbols]))
        
        for date in all_dates:
            should_stop, reason = self.risk_manager.should_stop_trading()
            if should_stop:
                print(f"Stopping backtest: {reason}")
                break
            
            for symbol in symbols:
                if symbol not in self.data:
                    continue
                
                df = self.data[symbol]
                if date not in df.index:
                    continue
                
                bar = df.loc[date]
                self.current_prices[symbol] = bar['close']
                
                bar_event = type('BarEvent', (), {
                    'symbol': symbol,
                    'timestamp': date,
                    'open': bar['open'],
                    'high': bar['high'],
                    'low': bar['low'],
                    'close': bar['close'],
                    'volume': bar['volume']
                })()
                
                signal = self.strategy.on_bar(bar_event)
                
                if signal:
                    self._process_signal(signal)
            
            self.portfolio.update_prices(self.current_prices)
        
        self.results = self._generate_results()
        return self.results
    
    def _process_signal(self, signal: Signal):
        symbol = signal.symbol
        price = signal.price
        
        if signal.signal_type == Signal.BUY:
            if not self.portfolio.has_position(symbol):
                quantity = self.risk_manager.calculate_position_size(price)
                
                if quantity > 0:
                    can_trade, reason = self.risk_manager.check_trade(symbol, quantity, price, "BUY")
                    
                    if can_trade:
                        execution_price = price * (1 + self.slippage)
                        self.portfolio.update_position(
                            symbol, quantity, execution_price, "BUY", self.commission
                        )
        
        elif signal.signal_type == Signal.SELL:
            if self.portfolio.has_position(symbol):
                position = self.portfolio.get_position(symbol)
                quantity = position.quantity
                
                can_trade, reason = self.risk_manager.check_trade(symbol, quantity, price, "SELL")
                
                if can_trade:
                    execution_price = price * (1 - self.slippage)
                    self.portfolio.update_position(
                        symbol, quantity, execution_price, "SELL", self.commission
                    )
    
    def _generate_results(self) -> dict:
        from src.risk.metrics import PerformanceMetrics
        
        metrics = PerformanceMetrics.calculate_all_metrics(
            self.portfolio.equity_curve,
            self.portfolio.trades,
            self.initial_capital
        )
        
        summary = self.portfolio.get_summary()
        
        results = {
            **metrics,
            'portfolio_summary': summary,
            'equity_curve': self.portfolio.equity_curve,
            'trades': self.portfolio.trades,
            'final_portfolio_value': self.portfolio.portfolio_value
        }
        
        return results
    
    def print_results(self):
        if not self.results:
            print("No results available. Run backtest first.")
            return
        
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        print(f"\nStrategy: {self.strategy.name}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Portfolio Value: ${self.results['final_portfolio_value']:,.2f}")
        print(f"Total Return: {self.results['total_return_pct']:.2f}%")
        print(f"\nRisk-Adjusted Performance:")
        print(f"  Sharpe Ratio: {self.results['sharpe_ratio']:.3f}")
        print(f"  Sortino Ratio: {self.results['sortino_ratio']:.3f}")
        print(f"  Calmar Ratio: {self.results['calmar_ratio']:.3f}")
        print(f"\nDrawdown Analysis:")
        print(f"  Max Drawdown: {self.results['max_drawdown_pct']:.2f}%")
        print(f"  Max Drawdown Duration: {self.results['max_drawdown_duration']} days")
        print(f"\nTrading Statistics:")
        print(f"  Total Trades: {self.results['total_trades']}")
        print(f"  Winning Trades: {self.results['winning_trades']}")
        print(f"  Losing Trades: {self.results['losing_trades']}")
        print(f"  Win Rate: {self.results['win_rate']:.2%}")
        print(f"  Average Win: ${self.results['avg_win']:.2f}")
        print(f"  Average Loss: ${self.results['avg_loss']:.2f}")
        print(f"  Profit Factor: {self.results['profit_factor']:.2f}")
        print(f"\nRisk Metrics:")
        print(f"  Value at Risk (95%): {self.results['value_at_risk_95']:.4f}")
        print(f"  Conditional VaR (95%): {self.results['cvar_95']:.4f}")
        print(f"\nBacktest Period: {self.results['trading_days']} days ({self.results['years']:.2f} years)")
        print("="*60 + "\n")
