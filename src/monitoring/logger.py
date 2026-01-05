import logging
import sys
from pathlib import Path
from datetime import datetime
from src.config import Config


class TradingLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        Config.ensure_dirs()
        
        self.logger = logging.getLogger('algo_trading')
        self.logger.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        log_file = Config.LOGS_DIR / f"trading_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def critical(self, message: str):
        self.logger.critical(message)
    
    def trade(self, action: str, symbol: str, quantity: int, price: float, reason: str = ""):
        message = f"TRADE: {action} {quantity} {symbol} @ ${price:.2f}"
        if reason:
            message += f" | Reason: {reason}"
        self.logger.info(message)
    
    def signal(self, signal_type: str, symbol: str, price: float, reason: str = ""):
        message = f"SIGNAL: {signal_type} {symbol} @ ${price:.2f}"
        if reason:
            message += f" | Reason: {reason}"
        self.logger.info(message)
    
    def performance(self, portfolio_value: float, cash: float, returns: float):
        message = f"PERFORMANCE: Portfolio=${portfolio_value:.2f}, Cash=${cash:.2f}, Return={returns:.2%}"
        self.logger.info(message)


def get_logger():
    return TradingLogger()
