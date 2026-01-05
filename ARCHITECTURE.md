# System Architecture

## Overview

This algorithmic trading system follows a modular, event-driven architecture designed for backtesting and paper trading. The system is built with extensibility, maintainability, and realistic simulation in mind.

## Core Architecture Principles

1. **Event-Driven Design**: Prevents look-ahead bias in backtesting
2. **Strategy Pattern**: Pluggable trading strategies
3. **Broker Abstraction**: Support for multiple brokers (virtual, Alpaca, etc.)
4. **Separation of Concerns**: Clear boundaries between modules
5. **Risk-First Approach**: Risk management integrated at every level

## System Layers

### 1. Data Layer (`src/data/`)

Responsible for fetching, storing, and streaming market data.

**Components:**

- **DataFetcher**: Retrieves historical OHLCV data from Yahoo Finance
  - Caches data to reduce API calls
  - Handles multiple symbols
  - Supports different timeframes

- **DataStore**: Persists market data in SQLite database
  - Efficient storage and retrieval
  - Indexed by symbol and timestamp
  - Prevents duplicate data

- **MarketFeed**: Streams market data for event-driven processing
  - Publish-subscribe pattern
  - Supports multiple subscribers
  - Historical and real-time data streams

**Data Flow:**
```
Yahoo Finance → DataFetcher → DataStore → MarketFeed → Strategy
```

### 2. Strategy Layer (`src/strategy/`)

Implements trading strategies with a consistent interface.

**Components:**

- **BaseStrategy**: Abstract base class defining strategy interface
  - `generate_signals()`: Batch signal generation for backtesting
  - `on_bar()`: Real-time signal generation
  - Position tracking
  - Signal history

- **Example Strategies**: Pre-built trading strategies
  - SMA Crossover: Moving average crossover signals
  - RSI: Overbought/oversold momentum strategy
  - Bollinger Bands: Mean reversion strategy
  - MACD: Trend-following strategy

**Strategy Interface:**
```python
class BaseStrategy(ABC):
    @abstractmethod
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> List[Signal]
    
    @abstractmethod
    def on_bar(self, bar_event) -> Optional[Signal]
```

### 3. Execution Layer (`src/execution/`)

Handles order creation, routing, and execution.

**Components:**

- **Order**: Data model for orders
  - Order types: Market, Limit, Stop, Stop-Limit
  - Order sides: Buy, Sell
  - Order status tracking
  - Fill information

- **Broker (Abstract)**: Interface for broker implementations
  - Submit/cancel orders
  - Query positions and account info
  - Get current prices

- **AlpacaBroker**: Alpaca API integration
  - Paper trading support
  - Real-time market data
  - Order execution via Alpaca

**Broker Interface:**
```python
class Broker(ABC):
    @abstractmethod
    def submit_order(self, order: Order) -> str
    
    @abstractmethod
    def get_account_info(self) -> dict
    
    @abstractmethod
    def get_positions(self) -> List[dict]
```

### 4. Risk Management Layer (`src/risk/`)

Manages portfolio risk and calculates performance metrics.

**Components:**

- **Portfolio**: Tracks positions, cash, and equity
  - Position management (FIFO)
  - Trade history
  - Equity curve tracking
  - P&L calculation

- **RiskManager**: Enforces risk rules
  - Position size limits
  - Drawdown protection
  - Cash availability checks
  - Pre-trade validation

- **PerformanceMetrics**: Calculates portfolio statistics
  - Sharpe ratio (risk-adjusted returns)
  - Sortino ratio (downside risk)
  - Max drawdown
  - Calmar ratio
  - Value at Risk (VaR)
  - Win rate, profit factor

**Risk Checks:**
```python
1. Check available cash
2. Check position size limit
3. Check portfolio drawdown
4. Calculate appropriate position size
5. Approve/reject trade
```

### 5. Backtesting Layer (`src/backtesting/`)

Simulates historical trading with realistic execution.

**Components:**

- **BacktestEngine**: Main backtesting loop
  - Event-driven simulation
  - Chronological order processing
  - Slippage and commission modeling
  - Multi-symbol support

- **EventLoop**: Event queue and dispatcher
  - Bar events
  - Signal events
  - Order events
  - Fill events

- **PerformanceAnalyzer**: Visualization and reporting
  - Equity curve plots
  - Drawdown charts
  - Returns distribution
  - Trade analysis

**Backtest Flow:**
```
Load Data → Generate Bar Events → Strategy Signals → Risk Check → Execute Orders → Update Portfolio → Repeat
```

### 6. Paper Trading Layer (`src/paper_trading/`)

Enables live trading with virtual money.

**Components:**

- **PaperTrader**: Main paper trading engine
  - Real-time data polling
  - Strategy execution
  - Position management
  - Performance tracking

- **VirtualBroker**: Simulated broker
  - No external API required
  - Realistic order execution
  - Portfolio tracking
  - Slippage simulation

**Paper Trading Flow:**
```
Poll Market Data → Update Prices → Generate Signals → Risk Check → Submit Orders → Update Positions → Log Performance → Repeat
```

### 7. Monitoring Layer (`src/monitoring/`)

Provides logging, metrics collection, and alerting.

**Components:**

- **Logger**: Structured logging
  - Console and file output
  - Trade logging
  - Signal logging
  - Performance logging

- **MetricsCollector**: Time-series metrics
  - Trade metrics
  - Portfolio snapshots
  - Signal history
  - JSON export

- **AlertSystem**: Risk alerts
  - Drawdown warnings
  - Position size alerts
  - Cash level alerts
  - Custom handlers

## Data Models

### Signal
```python
{
    'symbol': str,
    'signal_type': 'BUY' | 'SELL' | 'HOLD',
    'timestamp': datetime,
    'price': float,
    'quantity': int,
    'reason': str
}
```

### Order
```python
{
    'order_id': str,
    'symbol': str,
    'order_type': OrderType,
    'side': OrderSide,
    'quantity': int,
    'price': float,
    'status': OrderStatus,
    'filled_price': float,
    'filled_quantity': int
}
```

### Position
```python
{
    'symbol': str,
    'quantity': int,
    'avg_price': float,
    'current_price': float,
    'market_value': float,
    'unrealized_pl': float
}
```

### Trade
```python
{
    'symbol': str,
    'side': 'BUY' | 'SELL',
    'quantity': int,
    'price': float,
    'timestamp': datetime,
    'commission': float,
    'pnl': float
}
```

## Configuration Management

Configuration is centralized in `src/config.py`:

```python
- API Keys (Alpaca, IEX, Alpha Vantage)
- Trading Parameters (capital, commission, slippage)
- Risk Parameters (max position size, max drawdown)
- Directory Paths (data, logs)
```

Environment variables override defaults via `.env` file.

## Execution Flow

### Backtesting Flow

```
1. User configures backtest parameters
2. DataFetcher retrieves historical data
3. BacktestEngine loads data for each symbol
4. For each timestamp:
   a. Create bar events for available symbols
   b. Strategy processes bars and generates signals
   c. RiskManager validates each signal
   d. If approved, execute trade with slippage/commission
   e. Update portfolio positions and cash
   f. Record trade in history
5. Calculate final performance metrics
6. Generate reports and visualizations
```

### Paper Trading Flow

```
1. User configures paper trading parameters
2. PaperTrader initializes strategy and broker
3. Main loop (runs at poll_interval):
   a. DataFetcher gets latest prices
   b. Update broker/portfolio with current prices
   c. Strategy processes current market state
   d. Generate buy/sell signals
   e. RiskManager validates signals
   f. Submit approved orders to broker
   g. Log performance metrics
   h. Print status update
4. On stop: Generate final summary
```

## Testing Strategy

The system includes comprehensive unit tests:

- **Strategy Tests**: Verify signal generation logic
- **Backtest Tests**: Validate simulation accuracy
- **Risk Manager Tests**: Ensure risk rules are enforced
- **Broker Tests**: Test order execution and position tracking

Run tests with: `pytest tests/ -v`

## Extension Points

The system is designed for easy extension:

1. **New Strategies**: Inherit from `BaseStrategy`
2. **New Brokers**: Implement `Broker` interface
3. **New Data Sources**: Extend `DataFetcher`
4. **Custom Metrics**: Add to `PerformanceMetrics`
5. **Alert Handlers**: Register with `AlertSystem`

## Performance Considerations

- **Data Caching**: Reduces API calls and improves speed
- **Vectorized Operations**: Uses pandas/numpy for calculations
- **Event-Driven**: Processes data chronologically (no look-ahead)
- **Database Indexing**: Fast data retrieval from SQLite
- **Memory Efficiency**: Streams data when possible

## Security Considerations

- **API Key Storage**: Environment variables, never committed
- **Paper Trading Only**: No real money risk by default
- **Input Validation**: All user inputs validated
- **Error Handling**: Graceful degradation on errors

## Future Enhancements

Potential areas for expansion:

1. **Options Trading**: Add support for options strategies
2. **Multi-Asset**: Support futures, forex, crypto
3. **Machine Learning**: ML-based strategy framework
4. **Optimization**: Genetic algorithm parameter optimization
5. **Live Trading**: Production broker integration
6. **Web Dashboard**: Real-time monitoring interface
7. **Cloud Deployment**: AWS/GCP hosting
8. **Backtesting Engine Improvements**: Walk-forward analysis, Monte Carlo simulation

## Dependencies

### Core Dependencies
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **yfinance**: Historical market data
- **alpaca-trade-api**: Alpaca broker integration

### Visualization
- **plotly**: Interactive charts
- **matplotlib**: Static plots

### Testing
- **pytest**: Unit testing framework
- **pytest-cov**: Code coverage reports

## Directory Structure

```
algo-trading-system/
├── src/                    # Source code
│   ├── data/              # Data management
│   ├── strategy/          # Trading strategies
│   ├── execution/         # Order execution
│   ├── risk/              # Risk management
│   ├── backtesting/       # Backtesting engine
│   ├── paper_trading/     # Paper trading
│   ├── monitoring/        # Logging and alerts
│   └── utils/             # Utility functions
├── tests/                 # Unit tests
├── notebooks/             # Jupyter notebooks
├── data/                  # Market data (SQLite)
├── logs/                  # Log files
├── main.py               # CLI entry point
└── requirements.txt      # Dependencies
```

## Conclusion

This architecture provides a solid foundation for algorithmic trading research and development. The modular design allows for easy testing of trading strategies while maintaining realistic execution simulation through comprehensive risk management and cost modeling.
