from datetime import datetime
from typing import List, Dict
import json
from pathlib import Path


class MetricsCollector:
    def __init__(self):
        self.metrics = []
        self.session_start = datetime.now()
    
    def record_metric(self, metric_type: str, data: dict):
        metric = {
            'timestamp': datetime.now().isoformat(),
            'type': metric_type,
            'data': data
        }
        self.metrics.append(metric)
    
    def record_trade(self, symbol: str, side: str, quantity: int, price: float,
                    commission: float = 0.0):
        self.record_metric('trade', {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'commission': commission,
            'total_value': quantity * price + commission
        })
    
    def record_signal(self, signal_type: str, symbol: str, price: float, reason: str = ""):
        self.record_metric('signal', {
            'signal_type': signal_type,
            'symbol': symbol,
            'price': price,
            'reason': reason
        })
    
    def record_portfolio_snapshot(self, portfolio_value: float, cash: float,
                                 positions: dict, returns: float):
        self.record_metric('portfolio_snapshot', {
            'portfolio_value': portfolio_value,
            'cash': cash,
            'positions': positions,
            'returns': returns
        })
    
    def record_risk_event(self, event_type: str, details: str):
        self.record_metric('risk_event', {
            'event_type': event_type,
            'details': details
        })
    
    def get_metrics(self, metric_type: str = None) -> List[Dict]:
        if metric_type:
            return [m for m in self.metrics if m['type'] == metric_type]
        return self.metrics
    
    def get_trade_summary(self) -> dict:
        trades = self.get_metrics('trade')
        
        if not trades:
            return {'total_trades': 0}
        
        buy_trades = [t for t in trades if t['data']['side'].upper() == 'BUY']
        sell_trades = [t for t in trades if t['data']['side'].upper() == 'SELL']
        
        total_value_traded = sum(t['data']['total_value'] for t in trades)
        total_commissions = sum(t['data']['commission'] for t in trades)
        
        return {
            'total_trades': len(trades),
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'total_value_traded': total_value_traded,
            'total_commissions': total_commissions
        }
    
    def save_to_file(self, filepath: str):
        Path(filepath).parent.mkdir(exist_ok=True, parents=True)
        
        with open(filepath, 'w') as f:
            json.dump({
                'session_start': self.session_start.isoformat(),
                'session_end': datetime.now().isoformat(),
                'metrics': self.metrics,
                'summary': self.get_trade_summary()
            }, f, indent=2)
    
    def clear(self):
        self.metrics = []
        self.session_start = datetime.now()
