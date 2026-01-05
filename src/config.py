import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
    ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    
    IEX_API_KEY = os.getenv("IEX_API_KEY", "")
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    
    INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL", "100000"))
    COMMISSION_PER_TRADE = float(os.getenv("COMMISSION_PER_TRADE", "0"))
    SLIPPAGE_PERCENT = float(os.getenv("SLIPPAGE_PERCENT", "0.001"))
    
    MAX_POSITION_SIZE = 0.10
    MAX_DRAWDOWN_THRESHOLD = 0.20
    RISK_FREE_RATE = 0.02
    
    @classmethod
    def ensure_dirs(cls):
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
