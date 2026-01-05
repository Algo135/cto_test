# Quick Start Guide

Get started with the Algorithmic Trading System in 5 minutes!

## Installation

### Option 1: Automated Setup (Recommended)

```bash
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up directories
- Copy environment configuration

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data logs

# Copy environment file
cp .env.example .env
```

## Your First Backtest

### Simple Example

Run the included example script:

```bash
python example_backtest.py
```

This will:
1. Fetch 6 months of SPY data
2. Run an SMA crossover strategy
3. Display performance metrics

### Using the CLI

```bash
python main.py \
  --mode backtest \
  --symbols SPY \
  --strategy sma \
  --start 2023-01-01 \
  --end 2024-01-01 \
  --capital 100000 \
  --plot
```

Output:
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
  ...
```

## Try Different Strategies

### RSI Strategy

```bash
python main.py \
  --mode backtest \
  --symbols SPY \
  --strategy rsi \
  --rsi-period 14 \
  --rsi-oversold 30 \
  --rsi-overbought 70
```

### Bollinger Bands

```bash
python main.py \
  --mode backtest \
  --symbols SPY \
  --strategy bollinger \
  --bb-period 20 \
  --bb-std 2.0
```

### MACD Strategy

```bash
python main.py \
  --mode backtest \
  --symbols SPY \
  --strategy macd \
  --macd-fast 12 \
  --macd-slow 26 \
  --macd-signal 9
```

## Multiple Symbols

Backtest a portfolio of stocks:

```bash
python main.py \
  --mode backtest \
  --symbols SPY QQQ IWM \
  --strategy sma \
  --plot
```

## Paper Trading

### Without API (Virtual Broker)

```bash
python main.py \
  --mode paper \
  --symbols SPY QQQ \
  --strategy sma \
  --interval 60
```

This will:
- Fetch real-time prices every 60 seconds
- Generate trading signals
- Execute virtual trades
- Display portfolio status

Press `Ctrl+C` to stop.

### With Alpaca API

1. Sign up at https://alpaca.markets (free paper trading)
2. Get your API keys
3. Edit `.env` file:

```
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
```

4. Run paper trading:

```bash
python main.py \
  --mode paper \
  --symbols SPY \
  --strategy rsi \
  --use-alpaca
```

## Python API Usage

### Basic Backtest

```python
from datetime import datetime, timedelta
from src.data.data_fetcher import DataFetcher
from src.strategy.example_strategies import SMAcrossoverStrategy
from src.backtesting.backtest_engine import BacktestEngine

# Fetch data
fetcher = DataFetcher()
data = fetcher.fetch_historical_data('SPY', '2023-01-01', '2024-01-01')

# Create strategy
strategy = SMAcrossoverStrategy(short_window=20, long_window=50)

# Run backtest
engine = BacktestEngine(strategy, initial_capital=100000)
engine.load_data('SPY', data)
results = engine.run(['SPY'])

# Print results
engine.print_results()
```

### Custom Strategy

```python
from src.strategy.base_strategy import BaseStrategy, Signal
import pandas as pd

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="MyCustomStrategy")
    
    def generate_signals(self, symbol: str, data: pd.DataFrame):
        signals = []
        # Your trading logic here
        return signals
    
    def on_bar(self, bar_event):
        # Real-time trading logic
        return None

# Use your strategy
strategy = MyStrategy()
engine = BacktestEngine(strategy)
# ... rest of backtest code
```

## Understanding the Output

### Key Metrics

- **Total Return**: Overall profit/loss percentage
- **Sharpe Ratio**: Risk-adjusted returns (>1 is good, >2 is excellent)
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Ratio of gross profit to gross loss (>1 means profitable)

### Performance Plots

When using `--plot`, three HTML files are generated:

1. `backtest_equity_curve.html` - Portfolio value over time
2. `backtest_drawdown.html` - Drawdown visualization
3. `backtest_returns.html` - Return distribution

Open these in a web browser to view interactive charts.

## Jupyter Notebooks

For interactive analysis:

```bash
jupyter notebook notebooks/backtest_example.ipynb
```

## Running Tests

Verify everything works:

```bash
pytest tests/ -v
```

## Common Issues

### Import Errors

Make sure virtual environment is activated:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### API Rate Limits

Yahoo Finance has rate limits. If you see errors:
- Add delays between requests
- Use cached data from SQLite

### No Data Retrieved

Check:
- Symbol is valid (e.g., 'SPY', not 'spy')
- Date range is reasonable
- Internet connection is active

## Next Steps

1. **Read the Documentation**: Check [README.md](README.md) for detailed info
2. **Explore Strategies**: Try different strategy parameters
3. **Customize**: Create your own trading strategies
4. **Paper Trade**: Test strategies in real-time
5. **Analyze**: Use notebooks for deeper analysis

## Getting Help

- Check [README.md](README.md) for detailed documentation
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Open an issue on GitHub for bugs/questions
- Read the source code - it's well documented!

## Quick Reference

### CLI Commands

```bash
# Backtest
python main.py --mode backtest --symbols SPY --strategy sma

# Paper trade
python main.py --mode paper --symbols SPY --strategy rsi

# Help
python main.py --help
```

### Strategy Parameters

| Strategy | Parameters |
|----------|-----------|
| SMA | `--sma-short 20 --sma-long 50` |
| RSI | `--rsi-period 14 --rsi-oversold 30 --rsi-overbought 70` |
| Bollinger | `--bb-period 20 --bb-std 2.0` |
| MACD | `--macd-fast 12 --macd-slow 26 --macd-signal 9` |

Happy Trading! 📈
