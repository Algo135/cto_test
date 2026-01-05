import pandas as pd
import numpy as np
from typing import List, Optional
from .base_strategy import BaseStrategy, Signal


class SMAcrossoverStrategy(BaseStrategy):
    def __init__(self, short_window: int = 20, long_window: int = 50):
        super().__init__(name=f"SMA_Crossover_{short_window}_{long_window}")
        self.short_window = short_window
        self.long_window = long_window
        self.price_history = {}
    
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> List[Signal]:
        signals = []
        df = data.copy()
        
        df['sma_short'] = df['close'].rolling(window=self.short_window).mean()
        df['sma_long'] = df['close'].rolling(window=self.long_window).mean()
        
        df['signal'] = 0
        df.loc[df['sma_short'] > df['sma_long'], 'signal'] = 1
        df.loc[df['sma_short'] < df['sma_long'], 'signal'] = -1
        
        df['position'] = df['signal'].diff()
        
        for timestamp, row in df.iterrows():
            if pd.notna(row['position']):
                if row['position'] > 0:
                    signals.append(Signal(
                        symbol=symbol,
                        signal_type=Signal.BUY,
                        timestamp=timestamp,
                        price=row['close'],
                        reason="SMA short crossed above long"
                    ))
                elif row['position'] < 0:
                    signals.append(Signal(
                        symbol=symbol,
                        signal_type=Signal.SELL,
                        timestamp=timestamp,
                        price=row['close'],
                        reason="SMA short crossed below long"
                    ))
        
        return signals
    
    def on_bar(self, bar_event) -> Optional[Signal]:
        symbol = bar_event.symbol
        
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(bar_event.close)
        
        if len(self.price_history[symbol]) < self.long_window:
            return None
        
        prices = self.price_history[symbol][-self.long_window:]
        sma_short = np.mean(prices[-self.short_window:])
        sma_long = np.mean(prices)
        
        prev_prices = self.price_history[symbol][-self.long_window-1:-1]
        if len(prev_prices) >= self.long_window:
            prev_sma_short = np.mean(prev_prices[-self.short_window:])
            prev_sma_long = np.mean(prev_prices)
            
            if prev_sma_short <= prev_sma_long and sma_short > sma_long:
                return Signal(
                    symbol=symbol,
                    signal_type=Signal.BUY,
                    timestamp=bar_event.timestamp,
                    price=bar_event.close,
                    reason="SMA short crossed above long"
                )
            elif prev_sma_short >= prev_sma_long and sma_short < sma_long:
                return Signal(
                    symbol=symbol,
                    signal_type=Signal.SELL,
                    timestamp=bar_event.timestamp,
                    price=bar_event.close,
                    reason="SMA short crossed below long"
                )
        
        return None


class RSIStrategy(BaseStrategy):
    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        super().__init__(name=f"RSI_{period}")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.price_history = {}
    
    def calculate_rsi(self, prices: pd.Series) -> pd.Series:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> List[Signal]:
        signals = []
        df = data.copy()
        
        df['rsi'] = self.calculate_rsi(df['close'])
        
        for i in range(1, len(df)):
            prev_rsi = df['rsi'].iloc[i-1]
            curr_rsi = df['rsi'].iloc[i]
            
            if pd.notna(prev_rsi) and pd.notna(curr_rsi):
                if prev_rsi <= self.oversold and curr_rsi > self.oversold:
                    signals.append(Signal(
                        symbol=symbol,
                        signal_type=Signal.BUY,
                        timestamp=df.index[i],
                        price=df['close'].iloc[i],
                        reason=f"RSI crossed above {self.oversold}"
                    ))
                elif prev_rsi >= self.overbought and curr_rsi < self.overbought:
                    signals.append(Signal(
                        symbol=symbol,
                        signal_type=Signal.SELL,
                        timestamp=df.index[i],
                        price=df['close'].iloc[i],
                        reason=f"RSI crossed below {self.overbought}"
                    ))
        
        return signals
    
    def on_bar(self, bar_event) -> Optional[Signal]:
        symbol = bar_event.symbol
        
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(bar_event.close)
        
        if len(self.price_history[symbol]) < self.period + 2:
            return None
        
        prices = pd.Series(self.price_history[symbol])
        rsi_values = self.calculate_rsi(prices)
        
        if len(rsi_values) >= 2:
            prev_rsi = rsi_values.iloc[-2]
            curr_rsi = rsi_values.iloc[-1]
            
            if pd.notna(prev_rsi) and pd.notna(curr_rsi):
                if prev_rsi <= self.oversold and curr_rsi > self.oversold:
                    return Signal(
                        symbol=symbol,
                        signal_type=Signal.BUY,
                        timestamp=bar_event.timestamp,
                        price=bar_event.close,
                        reason=f"RSI crossed above {self.oversold}"
                    )
                elif prev_rsi >= self.overbought and curr_rsi < self.overbought:
                    return Signal(
                        symbol=symbol,
                        signal_type=Signal.SELL,
                        timestamp=bar_event.timestamp,
                        price=bar_event.close,
                        reason=f"RSI crossed below {self.overbought}"
                    )
        
        return None


class BollingerBandsStrategy(BaseStrategy):
    def __init__(self, period: int = 20, num_std: float = 2.0):
        super().__init__(name=f"Bollinger_Bands_{period}")
        self.period = period
        self.num_std = num_std
        self.price_history = {}
    
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> List[Signal]:
        signals = []
        df = data.copy()
        
        df['sma'] = df['close'].rolling(window=self.period).mean()
        df['std'] = df['close'].rolling(window=self.period).std()
        df['upper_band'] = df['sma'] + (df['std'] * self.num_std)
        df['lower_band'] = df['sma'] - (df['std'] * self.num_std)
        
        for i in range(1, len(df)):
            if pd.notna(df['lower_band'].iloc[i]):
                prev_close = df['close'].iloc[i-1]
                curr_close = df['close'].iloc[i]
                lower_band = df['lower_band'].iloc[i]
                upper_band = df['upper_band'].iloc[i]
                
                if prev_close >= lower_band and curr_close < lower_band:
                    signals.append(Signal(
                        symbol=symbol,
                        signal_type=Signal.BUY,
                        timestamp=df.index[i],
                        price=curr_close,
                        reason="Price touched lower Bollinger Band"
                    ))
                elif prev_close <= upper_band and curr_close > upper_band:
                    signals.append(Signal(
                        symbol=symbol,
                        signal_type=Signal.SELL,
                        timestamp=df.index[i],
                        price=curr_close,
                        reason="Price touched upper Bollinger Band"
                    ))
        
        return signals
    
    def on_bar(self, bar_event) -> Optional[Signal]:
        symbol = bar_event.symbol
        
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(bar_event.close)
        
        if len(self.price_history[symbol]) < self.period + 1:
            return None
        
        prices = self.price_history[symbol][-self.period-1:]
        sma = np.mean(prices[-self.period:])
        std = np.std(prices[-self.period:])
        upper_band = sma + (std * self.num_std)
        lower_band = sma - (std * self.num_std)
        
        prev_close = prices[-2]
        curr_close = prices[-1]
        
        if prev_close >= lower_band and curr_close < lower_band:
            return Signal(
                symbol=symbol,
                signal_type=Signal.BUY,
                timestamp=bar_event.timestamp,
                price=bar_event.close,
                reason="Price touched lower Bollinger Band"
            )
        elif prev_close <= upper_band and curr_close > upper_band:
            return Signal(
                symbol=symbol,
                signal_type=Signal.SELL,
                timestamp=bar_event.timestamp,
                price=bar_event.close,
                reason="Price touched upper Bollinger Band"
            )
        
        return None


class MACDStrategy(BaseStrategy):
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        super().__init__(name=f"MACD_{fast_period}_{slow_period}_{signal_period}")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.price_history = {}
    
    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        return prices.ewm(span=period, adjust=False).mean()
    
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> List[Signal]:
        signals = []
        df = data.copy()
        
        df['ema_fast'] = self.calculate_ema(df['close'], self.fast_period)
        df['ema_slow'] = self.calculate_ema(df['close'], self.slow_period)
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['signal_line'] = self.calculate_ema(df['macd'], self.signal_period)
        
        for i in range(1, len(df)):
            if pd.notna(df['signal_line'].iloc[i]):
                prev_macd = df['macd'].iloc[i-1]
                curr_macd = df['macd'].iloc[i]
                prev_signal = df['signal_line'].iloc[i-1]
                curr_signal = df['signal_line'].iloc[i]
                
                if prev_macd <= prev_signal and curr_macd > curr_signal:
                    signals.append(Signal(
                        symbol=symbol,
                        signal_type=Signal.BUY,
                        timestamp=df.index[i],
                        price=df['close'].iloc[i],
                        reason="MACD crossed above signal line"
                    ))
                elif prev_macd >= prev_signal and curr_macd < curr_signal:
                    signals.append(Signal(
                        symbol=symbol,
                        signal_type=Signal.SELL,
                        timestamp=df.index[i],
                        price=df['close'].iloc[i],
                        reason="MACD crossed below signal line"
                    ))
        
        return signals
    
    def on_bar(self, bar_event) -> Optional[Signal]:
        symbol = bar_event.symbol
        
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(bar_event.close)
        
        min_required = self.slow_period + self.signal_period + 1
        if len(self.price_history[symbol]) < min_required:
            return None
        
        prices = pd.Series(self.price_history[symbol])
        ema_fast = self.calculate_ema(prices, self.fast_period)
        ema_slow = self.calculate_ema(prices, self.slow_period)
        macd = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd, self.signal_period)
        
        if len(signal_line) >= 2:
            prev_macd = macd.iloc[-2]
            curr_macd = macd.iloc[-1]
            prev_signal = signal_line.iloc[-2]
            curr_signal = signal_line.iloc[-1]
            
            if pd.notna(prev_signal) and pd.notna(curr_signal):
                if prev_macd <= prev_signal and curr_macd > curr_signal:
                    return Signal(
                        symbol=symbol,
                        signal_type=Signal.BUY,
                        timestamp=bar_event.timestamp,
                        price=bar_event.close,
                        reason="MACD crossed above signal line"
                    )
                elif prev_macd >= prev_signal and curr_macd < curr_signal:
                    return Signal(
                        symbol=symbol,
                        signal_type=Signal.SELL,
                        timestamp=bar_event.timestamp,
                        price=bar_event.close,
                        reason="MACD crossed below signal line"
                    )
        
        return None
