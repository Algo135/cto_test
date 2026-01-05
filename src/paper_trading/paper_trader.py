import time
from datetime import datetime
from typing import List, Optional
from src.strategy.base_strategy import BaseStrategy, Signal
from src.execution.alpaca_broker import AlpacaBroker
from src.execution.order import Order, OrderType, OrderSide
from src.risk.risk_manager import RiskManager
from src.risk.portfolio import Portfolio
from src.data.data_fetcher import DataFetcher


class PaperTrader:
    def __init__(
        self,
        strategy: BaseStrategy,
        symbols: List[str],
        use_alpaca: bool = True,
        initial_capital: float = 100000
    ):
        self.strategy = strategy
        self.symbols = symbols
        self.is_running = False
        
        if use_alpaca:
            try:
                self.broker = AlpacaBroker()
                print("Connected to Alpaca paper trading")
            except Exception as e:
                print(f"Failed to connect to Alpaca: {str(e)}")
                print("Using virtual broker instead")
                from .virtual_broker import VirtualBroker
                self.broker = VirtualBroker(initial_capital)
        else:
            from .virtual_broker import VirtualBroker
            self.broker = VirtualBroker(initial_capital)
        
        self.data_fetcher = DataFetcher()
        self.portfolio = Portfolio(initial_capital)
        self.risk_manager = RiskManager(self.portfolio)
        
        self.performance_log = []
    
    def start(self, poll_interval: int = 60):
        print(f"\nStarting paper trading for symbols: {', '.join(self.symbols)}")
        print(f"Poll interval: {poll_interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        self.is_running = True
        
        try:
            while self.is_running:
                self._trading_iteration()
                
                time.sleep(poll_interval)
        
        except KeyboardInterrupt:
            print("\nStopping paper trading...")
            self.stop()
        except Exception as e:
            print(f"Error in paper trading: {str(e)}")
            self.stop()
    
    def _trading_iteration(self):
        should_stop, reason = self.risk_manager.should_stop_trading()
        if should_stop:
            print(f"Stopping trading: {reason}")
            self.stop()
            return
        
        current_prices = {}
        for symbol in self.symbols:
            price = self.data_fetcher.fetch_latest_price(symbol)
            if price:
                current_prices[symbol] = price
        
        if hasattr(self.broker, 'update_prices'):
            self.broker.update_prices(current_prices)
        
        self.portfolio.update_prices(current_prices)
        
        for symbol in self.symbols:
            if symbol not in current_prices:
                continue
            
            bar_event = type('BarEvent', (), {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'open': current_prices[symbol],
                'high': current_prices[symbol],
                'low': current_prices[symbol],
                'close': current_prices[symbol],
                'volume': 0
            })()
            
            signal = self.strategy.on_bar(bar_event)
            
            if signal:
                self._process_signal(signal, current_prices[symbol])
        
        self._log_performance()
        self._print_status()
    
    def _process_signal(self, signal: Signal, current_price: float):
        symbol = signal.symbol
        
        if signal.signal_type == Signal.BUY:
            if not self.portfolio.has_position(symbol):
                quantity = self.risk_manager.calculate_position_size(current_price)
                
                if quantity > 0:
                    can_trade, reason = self.risk_manager.check_trade(
                        symbol, quantity, current_price, "BUY"
                    )
                    
                    if can_trade:
                        order = Order(
                            symbol=symbol,
                            order_type=OrderType.MARKET,
                            side=OrderSide.BUY,
                            quantity=quantity
                        )
                        
                        try:
                            order_id = self.broker.submit_order(order)
                            print(f"\n✅ BUY order submitted: {quantity} shares of {symbol} @ ~${current_price:.2f}")
                            print(f"   Reason: {signal.reason}")
                        except Exception as e:
                            print(f"\n❌ Failed to submit BUY order for {symbol}: {str(e)}")
                    else:
                        print(f"\n⚠️  Trade rejected: {reason}")
        
        elif signal.signal_type == Signal.SELL:
            if self.portfolio.has_position(symbol):
                position = self.portfolio.get_position(symbol)
                quantity = position.quantity
                
                can_trade, reason = self.risk_manager.check_trade(
                    symbol, quantity, current_price, "SELL"
                )
                
                if can_trade:
                    order = Order(
                        symbol=symbol,
                        order_type=OrderType.MARKET,
                        side=OrderSide.SELL,
                        quantity=quantity
                    )
                    
                    try:
                        order_id = self.broker.submit_order(order)
                        print(f"\n✅ SELL order submitted: {quantity} shares of {symbol} @ ~${current_price:.2f}")
                        print(f"   Reason: {signal.reason}")
                    except Exception as e:
                        print(f"\n❌ Failed to submit SELL order for {symbol}: {str(e)}")
                else:
                    print(f"\n⚠️  Trade rejected: {reason}")
    
    def _log_performance(self):
        account_info = self.broker.get_account_info()
        
        self.performance_log.append({
            'timestamp': datetime.now(),
            'portfolio_value': account_info.get('portfolio_value', 0),
            'cash': account_info.get('cash', 0),
            'positions': len(self.broker.get_positions())
        })
    
    def _print_status(self):
        account_info = self.broker.get_account_info()
        positions = self.broker.get_positions()
        
        print(f"\n{'='*60}")
        print(f"Paper Trading Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        print(f"Portfolio Value: ${account_info.get('portfolio_value', 0):,.2f}")
        print(f"Cash: ${account_info.get('cash', 0):,.2f}")
        print(f"Total Return: {account_info.get('total_return', 0):.2%}")
        print(f"Drawdown: {account_info.get('drawdown', 0):.2%}")
        print(f"\nPositions ({len(positions)}):")
        
        for pos in positions:
            print(f"  {pos['symbol']}: {pos['quantity']} shares @ ${pos['avg_entry_price']:.2f}")
            print(f"    Current: ${pos['current_price']:.2f} | P&L: ${pos['unrealized_pl']:.2f}")
        
        if not positions:
            print("  No open positions")
        
        print(f"{'='*60}\n")
    
    def stop(self):
        self.is_running = False
        print("\n" + "="*60)
        print("PAPER TRADING SESSION ENDED")
        print("="*60)
        
        summary = self.portfolio.get_summary()
        print(f"\nFinal Portfolio Value: ${summary['portfolio_value']:,.2f}")
        print(f"Total Return: {summary['total_return_pct']:.2f}%")
        print(f"Total Trades: {summary['total_trades']}")
        print(f"Win Rate: {summary['win_rate']:.2%}")
        print("="*60 + "\n")
    
    def get_performance_summary(self) -> dict:
        account_info = self.broker.get_account_info()
        summary = self.portfolio.get_summary()
        
        return {
            **account_info,
            **summary,
            'performance_log': self.performance_log
        }
