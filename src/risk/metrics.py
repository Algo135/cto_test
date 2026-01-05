import numpy as np
import pandas as pd
from typing import List


class PerformanceMetrics:
    @staticmethod
    def calculate_returns(equity_curve: List[dict]) -> pd.Series:
        if not equity_curve:
            return pd.Series()
        
        values = [point['value'] for point in equity_curve]
        returns = pd.Series(values).pct_change().dropna()
        return returns
    
    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02,
                    periods_per_year: int = 252) -> float:
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / periods_per_year)
        return np.sqrt(periods_per_year) * (excess_returns.mean() / returns.std())
    
    @staticmethod
    def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02,
                     periods_per_year: int = 252) -> float:
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / periods_per_year)
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        return np.sqrt(periods_per_year) * (excess_returns.mean() / downside_returns.std())
    
    @staticmethod
    def max_drawdown(equity_curve: List[dict]) -> tuple[float, int]:
        if not equity_curve:
            return 0.0, 0
        
        values = [point['value'] for point in equity_curve]
        peak = values[0]
        max_dd = 0.0
        max_dd_duration = 0
        current_dd_duration = 0
        
        for value in values:
            if value > peak:
                peak = value
                current_dd_duration = 0
            else:
                drawdown = (peak - value) / peak
                max_dd = max(max_dd, drawdown)
                current_dd_duration += 1
                max_dd_duration = max(max_dd_duration, current_dd_duration)
        
        return max_dd, max_dd_duration
    
    @staticmethod
    def calmar_ratio(total_return: float, max_drawdown: float, years: float) -> float:
        if max_drawdown == 0 or years == 0:
            return 0.0
        
        annual_return = (1 + total_return) ** (1 / years) - 1
        return annual_return / max_drawdown
    
    @staticmethod
    def value_at_risk(returns: pd.Series, confidence_level: float = 0.95) -> float:
        if len(returns) == 0:
            return 0.0
        
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    @staticmethod
    def conditional_value_at_risk(returns: pd.Series, confidence_level: float = 0.95) -> float:
        if len(returns) == 0:
            return 0.0
        
        var = PerformanceMetrics.value_at_risk(returns, confidence_level)
        return returns[returns <= var].mean()
    
    @staticmethod
    def calculate_all_metrics(equity_curve: List[dict], trades: List,
                            initial_capital: float, risk_free_rate: float = 0.02) -> dict:
        returns = PerformanceMetrics.calculate_returns(equity_curve)
        
        if not equity_curve:
            return {}
        
        final_value = equity_curve[-1]['value']
        total_return = (final_value - initial_capital) / initial_capital
        
        max_dd, max_dd_duration = PerformanceMetrics.max_drawdown(equity_curve)
        
        trading_days = len(equity_curve)
        years = trading_days / 252
        
        winning_trades = [t for t in trades if hasattr(t, 'pnl') and t.pnl > 0]
        losing_trades = [t for t in trades if hasattr(t, 'pnl') and t.pnl < 0]
        
        return {
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'sharpe_ratio': PerformanceMetrics.sharpe_ratio(returns, risk_free_rate),
            'sortino_ratio': PerformanceMetrics.sortino_ratio(returns, risk_free_rate),
            'max_drawdown': max_dd,
            'max_drawdown_pct': max_dd * 100,
            'max_drawdown_duration': max_dd_duration,
            'calmar_ratio': PerformanceMetrics.calmar_ratio(total_return, max_dd, years),
            'value_at_risk_95': PerformanceMetrics.value_at_risk(returns, 0.95),
            'cvar_95': PerformanceMetrics.conditional_value_at_risk(returns, 0.95),
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(trades) if trades else 0,
            'avg_win': np.mean([t.pnl for t in winning_trades]) if winning_trades else 0,
            'avg_loss': np.mean([t.pnl for t in losing_trades]) if losing_trades else 0,
            'profit_factor': (abs(sum(t.pnl for t in winning_trades)) / 
                            abs(sum(t.pnl for t in losing_trades))) if losing_trades else 0,
            'trading_days': trading_days,
            'years': years
        }
