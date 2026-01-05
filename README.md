# Algorithmic Trading System

A comprehensive Python-based algorithmic trading system with backtesting and paper trading capabilities for stock market trading.

## 🚀 Features

- **Multiple Trading Strategies**: SMA Crossover, RSI, Bollinger Bands, MACD
- **Historical Backtesting**: Test strategies against years of market data
- **Paper Trading**: Practice trading with real-time data without risking real money
- **Risk Management**: Position sizing, drawdown limits, portfolio risk checks
- **Performance Analytics**: Sharpe ratio, Sortino ratio, max drawdown, win rate, and more
- **Data Management**: Fetch, store, and manage historical market data
- **Broker Integration**: Alpaca API support for paper trading
- **Monitoring & Logging**: Comprehensive logging and alerting system
- **Visualization**: Interactive charts for equity curves, drawdowns, and performance

## 📁 Project Structure

```
algo-trading-system/
├── src/
│   ├── config.py                 # Configuration management
│   ├── data/                     # Data fetching and storage
│   ├── strategy/                 # Trading strategies
│   ├── execution/                # Order execution and brokers
│   ├── risk/                     # Portfolio and risk management
│   ├── backtesting/              # Backtesting engine
│   ├── paper_trading/            # Paper trading engine
│   ├── monitoring/               # Logging and alerts
│   └── utils/                    # Utility functions
├── tests/                        # Unit tests
├── notebooks/                    # Example Jupyter notebooks
├── main.py                       # CLI entry point
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd algo-trading-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys (optional, for paper trading with Alpaca):
```bash
cp .env.example .env
# Edit .env and add your Alpaca API keys
```

## 📚 Quick Start

### Running a Backtest

Test the SMA Crossover strategy on SPY for the past year:

```bash
python main.py --mode backtest --symbols SPY --strategy sma --start 2023-01-01 --end 2024-01-01 --plot
```

### Paper Trading

Start paper trading with the RSI strategy:

```bash
python main.py --mode paper --symbols SPY QQQ --strategy rsi --interval 60
```

### Using Alpaca API for Paper Trading

```bash
python main.py --mode paper --symbols SPY --strategy macd --use-alpaca
```

## 🎯 Strategies

### 1. SMA Crossover Strategy

Trades based on simple moving average crossovers.

```bash
python main.py --mode backtest --strategy sma --sma-short 20 --sma-long 50
```

Parameters:
- `--sma-short`: Short-term SMA window (default: 20)
- `--sma-long`: Long-term SMA window (default: 50)

### 2. RSI Strategy

Trades based on Relative Strength Index overbought/oversold conditions.

```bash
python main.py --mode backtest --strategy rsi --rsi-period 14 --rsi-oversold 30 --rsi-overbought 70
```

Parameters:
- `--rsi-period`: RSI calculation period (default: 14)
- `--rsi-oversold`: Oversold threshold (default: 30)
- `--rsi-overbought`: Overbought threshold (default: 70)

### 3. Bollinger Bands Strategy

Mean reversion strategy using Bollinger Bands.

```bash
python main.py --mode backtest --strategy bollinger --bb-period 20 --bb-std 2.0
```

Parameters:
- `--bb-period`: Moving average period (default: 20)
- `--bb-std`: Standard deviations (default: 2.0)

### 4. MACD Strategy

Trades based on MACD crossovers.

```bash
python main.py --mode backtest --strategy macd --macd-fast 12 --macd-slow 26 --macd-signal 9
```

Parameters:
- `--macd-fast`: Fast EMA period (default: 12)
- `--macd-slow`: Slow EMA period (default: 26)
- `--macd-signal`: Signal line period (default: 9)

## 📊 Performance Metrics

The system calculates comprehensive performance metrics:

- **Total Return**: Overall profit/loss percentage
- **Sharpe Ratio**: Risk-adjusted return metric
- **Sortino Ratio**: Downside risk-adjusted return
- **Calmar Ratio**: Return relative to maximum drawdown
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Ratio of gross profit to gross loss
- **Value at Risk (VaR)**: Potential loss at 95% confidence level

## 🛡️ Risk Management

The system includes built-in risk management features:

- **Position Sizing**: Automatic calculation based on risk parameters
- **Maximum Position Size**: Limit individual position to % of portfolio (default: 10%)
- **Drawdown Protection**: Stop trading if drawdown exceeds threshold (default: 20%)
- **Commission & Slippage**: Realistic cost modeling
- **Stop-Loss Support**: Configurable stop-loss orders

## 📈 Backtesting

### Example: Backtest SPY with Multiple Strategies

```python
from src.data.data_fetcher import DataFetcher
from src.strategy.example_strategies import SMAcrossoverStrategy
from src.backtesting.backtest_engine import BacktestEngine

# Fetch data
fetcher = DataFetcher()
data = fetcher.fetch_historical_data('SPY', '2023-01-01', '2024-01-01')

# Create strategy and engine
strategy = SMAcrossoverStrategy(20, 50)
engine = BacktestEngine(strategy, initial_capital=100000)

# Run backtest
engine.load_data('SPY', data)
results = engine.run(['SPY'])
engine.print_results()
```

### Backtesting Features

- **Realistic Execution**: Includes slippage and commission
- **Event-Driven Architecture**: Prevents look-ahead bias
- **Multiple Symbols**: Trade multiple stocks simultaneously
- **Performance Visualization**: Generate interactive charts

## 🎮 Paper Trading

Paper trading allows you to test strategies in real-time without risking real money.

### Virtual Broker (No API Required)

```bash
python main.py --mode paper --symbols SPY QQQ --strategy sma --interval 60
```

### Alpaca Integration (Requires API Keys)

1. Sign up for Alpaca paper trading account at https://alpaca.markets
2. Get your API keys
3. Add keys to `.env` file:
```
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key
```

4. Run paper trading:
```bash
python main.py --mode paper --symbols SPY --strategy rsi --use-alpaca
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## 📓 Jupyter Notebooks

Example notebooks are provided in the `notebooks/` directory:

- `backtest_example.ipynb`: Complete backtesting workflow
- `performance_analysis.ipynb`: Advanced performance analysis

To use:

```bash
jupyter notebook notebooks/backtest_example.ipynb
```

## 🔧 Configuration

Edit `src/config.py` or use environment variables:

```python
INITIAL_CAPITAL = 100000          # Starting capital
COMMISSION_PER_TRADE = 0          # Commission per trade
SLIPPAGE_PERCENT = 0.001          # Slippage (0.1%)
MAX_POSITION_SIZE = 0.10          # Max 10% per position
MAX_DRAWDOWN_THRESHOLD = 0.20     # Stop at 20% drawdown
RISK_FREE_RATE = 0.02             # 2% risk-free rate
```

## 📝 Command Line Options

### Common Options

- `--mode`: `backtest` or `paper` (default: backtest)
- `--symbols`: Space-separated list of stock symbols
- `--strategy`: Strategy to use (`sma`, `rsi`, `bollinger`, `macd`)
- `--capital`: Initial capital (default: 100000)

### Backtest-Specific Options

- `--start`: Start date (YYYY-MM-DD)
- `--end`: End date (YYYY-MM-DD)
- `--commission`: Commission per trade
- `--slippage`: Slippage percentage
- `--plot`: Generate performance plots

### Paper Trading-Specific Options

- `--interval`: Poll interval in seconds (default: 60)
- `--use-alpaca`: Use Alpaca API instead of virtual broker

## 📊 Example Output

```
============================================================
BACKTEST RESULTS
============================================================

Strategy: SMA_Crossover_20_50
Initial Capital: $100,000.00
Final Portfolio Value: $112,450.00
Total Return: 12.45%

Risk-Adjusted Performance:
  Sharpe Ratio: 1.234
  Sortino Ratio: 1.567
  Calmar Ratio: 0.890

Drawdown Analysis:
  Max Drawdown: 8.45%
  Max Drawdown Duration: 23 days

Trading Statistics:
  Total Trades: 45
  Winning Trades: 28
  Losing Trades: 17
  Win Rate: 62.22%
  Average Win: $524.30
  Average Loss: $-312.50
  Profit Factor: 1.85

Risk Metrics:
  Value at Risk (95%): -0.0156
  Conditional VaR (95%): -0.0234

Backtest Period: 252 days (1.00 years)
============================================================
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Disclaimer

This software is for educational purposes only. Do not use this for actual trading without thorough testing and understanding of the risks involved. Trading stocks carries significant risk of loss.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Yahoo Finance for market data
- Alpaca for paper trading API
- Open-source Python trading community

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Happy Trading! 📈**
