import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple


def parse_date(date_str: str) -> datetime:
    formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%Y%m%d'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


def calculate_date_range(period: str) -> Tuple[str, str]:
    end_date = datetime.now()
    
    if period == '1M':
        start_date = end_date - timedelta(days=30)
    elif period == '3M':
        start_date = end_date - timedelta(days=90)
    elif period == '6M':
        start_date = end_date - timedelta(days=180)
    elif period == '1Y':
        start_date = end_date - timedelta(days=365)
    elif period == '2Y':
        start_date = end_date - timedelta(days=730)
    elif period == '5Y':
        start_date = end_date - timedelta(days=1825)
    else:
        start_date = end_date - timedelta(days=365)
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    return f"{value:.2%}"


def calculate_correlation(series1: pd.Series, series2: pd.Series) -> float:
    if len(series1) != len(series2):
        raise ValueError("Series must have the same length")
    
    return series1.corr(series2)


def resample_data(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    resampled = df.resample(timeframe).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })
    
    return resampled.dropna()


def normalize_symbol(symbol: str) -> str:
    return symbol.upper().strip()


def validate_symbols(symbols: List[str]) -> List[str]:
    return [normalize_symbol(s) for s in symbols if s and len(s) <= 5]


def calculate_position_value(quantity: int, price: float) -> float:
    return quantity * price


def calculate_pnl(entry_price: float, exit_price: float, quantity: int,
                 side: str = "long") -> float:
    if side.lower() == "long":
        return (exit_price - entry_price) * quantity
    elif side.lower() == "short":
        return (entry_price - exit_price) * quantity
    else:
        raise ValueError(f"Invalid side: {side}")


def annualize_return(total_return: float, days: int) -> float:
    if days <= 0:
        return 0.0
    
    years = days / 365.0
    return (1 + total_return) ** (1 / years) - 1


def calculate_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    if len(returns) == 0:
        return 0.0
    
    return returns.std() * np.sqrt(periods_per_year)
