from datetime import datetime
from typing import Callable, List
from enum import Enum


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Alert:
    def __init__(self, level: AlertLevel, message: str, details: dict = None):
        self.timestamp = datetime.now()
        self.level = level
        self.message = message
        self.details = details or {}
    
    def __repr__(self):
        return f"Alert({self.level.value.upper()}: {self.message} at {self.timestamp})"


class AlertSystem:
    def __init__(self):
        self.alerts: List[Alert] = []
        self.handlers: List[Callable] = []
    
    def add_handler(self, handler: Callable):
        self.handlers.append(handler)
    
    def trigger_alert(self, level: AlertLevel, message: str, details: dict = None):
        alert = Alert(level, message, details)
        self.alerts.append(alert)
        
        for handler in self.handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"Error in alert handler: {str(e)}")
    
    def check_drawdown(self, current_drawdown: float, max_drawdown: float):
        if current_drawdown > max_drawdown * 0.8:
            self.trigger_alert(
                AlertLevel.WARNING,
                f"Drawdown approaching maximum threshold",
                {'current_drawdown': current_drawdown, 'max_drawdown': max_drawdown}
            )
        
        if current_drawdown > max_drawdown:
            self.trigger_alert(
                AlertLevel.CRITICAL,
                f"Maximum drawdown threshold exceeded",
                {'current_drawdown': current_drawdown, 'max_drawdown': max_drawdown}
            )
    
    def check_position_size(self, position_value: float, portfolio_value: float,
                          max_position_size: float):
        position_pct = position_value / portfolio_value
        
        if position_pct > max_position_size:
            self.trigger_alert(
                AlertLevel.WARNING,
                f"Position size exceeds maximum",
                {
                    'position_value': position_value,
                    'portfolio_value': portfolio_value,
                    'position_pct': position_pct,
                    'max_position_size': max_position_size
                }
            )
    
    def check_cash_level(self, cash: float, min_cash_pct: float, portfolio_value: float):
        cash_pct = cash / portfolio_value
        
        if cash_pct < min_cash_pct:
            self.trigger_alert(
                AlertLevel.WARNING,
                f"Cash level below minimum threshold",
                {
                    'cash': cash,
                    'cash_pct': cash_pct,
                    'min_cash_pct': min_cash_pct
                }
            )
    
    def get_alerts(self, level: AlertLevel = None) -> List[Alert]:
        if level:
            return [a for a in self.alerts if a.level == level]
        return self.alerts
    
    def clear_alerts(self):
        self.alerts = []


def console_alert_handler(alert: Alert):
    prefix = {
        AlertLevel.INFO: "ℹ️ ",
        AlertLevel.WARNING: "⚠️ ",
        AlertLevel.ERROR: "❌",
        AlertLevel.CRITICAL: "🚨"
    }.get(alert.level, "")
    
    print(f"\n{prefix} {alert.level.value.upper()}: {alert.message}")
    if alert.details:
        for key, value in alert.details.items():
            print(f"  {key}: {value}")
    print()
