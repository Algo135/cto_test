from datetime import datetime
from typing import List


class ValidationError(Exception):
    pass


def validate_symbol(symbol: str) -> bool:
    if not symbol:
        raise ValidationError("Symbol cannot be empty")
    
    if not isinstance(symbol, str):
        raise ValidationError("Symbol must be a string")
    
    if len(symbol) > 5:
        raise ValidationError("Symbol must be 5 characters or less")
    
    if not symbol.isalpha():
        raise ValidationError("Symbol must contain only letters")
    
    return True


def validate_symbols(symbols: List[str]) -> bool:
    if not symbols:
        raise ValidationError("Symbols list cannot be empty")
    
    if not isinstance(symbols, list):
        raise ValidationError("Symbols must be a list")
    
    for symbol in symbols:
        validate_symbol(symbol)
    
    return True


def validate_date_range(start_date: str, end_date: str) -> bool:
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise ValidationError("Dates must be in YYYY-MM-DD format")
    
    if start >= end:
        raise ValidationError("Start date must be before end date")
    
    if end > datetime.now():
        raise ValidationError("End date cannot be in the future")
    
    return True


def validate_capital(capital: float) -> bool:
    if not isinstance(capital, (int, float)):
        raise ValidationError("Capital must be a number")
    
    if capital <= 0:
        raise ValidationError("Capital must be positive")
    
    if capital < 1000:
        raise ValidationError("Capital must be at least $1,000")
    
    return True


def validate_quantity(quantity: int) -> bool:
    if not isinstance(quantity, int):
        raise ValidationError("Quantity must be an integer")
    
    if quantity <= 0:
        raise ValidationError("Quantity must be positive")
    
    return True


def validate_price(price: float) -> bool:
    if not isinstance(price, (int, float)):
        raise ValidationError("Price must be a number")
    
    if price <= 0:
        raise ValidationError("Price must be positive")
    
    return True


def validate_percentage(value: float, min_val: float = 0.0, max_val: float = 1.0) -> bool:
    if not isinstance(value, (int, float)):
        raise ValidationError("Percentage must be a number")
    
    if value < min_val or value > max_val:
        raise ValidationError(f"Percentage must be between {min_val} and {max_val}")
    
    return True


def validate_strategy_params(params: dict) -> bool:
    if not isinstance(params, dict):
        raise ValidationError("Strategy parameters must be a dictionary")
    
    return True
