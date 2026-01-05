import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class PerformanceAnalyzer:
    def __init__(self, backtest_results: dict):
        self.results = backtest_results
    
    def plot_equity_curve(self, show: bool = True, save_path: str = None):
        equity_curve = self.results.get('equity_curve', [])
        
        if not equity_curve:
            print("No equity curve data available")
            return
        
        timestamps = [point['timestamp'] for point in equity_curve]
        values = [point['value'] for point in equity_curve]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=values,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='blue', width=2)
        ))
        
        fig.update_layout(
            title='Portfolio Equity Curve',
            xaxis_title='Date',
            yaxis_title='Portfolio Value ($)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        if save_path:
            fig.write_html(save_path)
        
        if show:
            fig.show()
        
        return fig
    
    def plot_drawdown(self, show: bool = True, save_path: str = None):
        equity_curve = self.results.get('equity_curve', [])
        
        if not equity_curve:
            print("No equity curve data available")
            return
        
        timestamps = [point['timestamp'] for point in equity_curve]
        values = [point['value'] for point in equity_curve]
        
        peak = values[0]
        drawdowns = []
        
        for value in values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            drawdowns.append(-dd * 100)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=drawdowns,
            mode='lines',
            name='Drawdown',
            line=dict(color='red', width=2),
            fill='tozeroy'
        ))
        
        fig.update_layout(
            title='Drawdown Over Time',
            xaxis_title='Date',
            yaxis_title='Drawdown (%)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        if save_path:
            fig.write_html(save_path)
        
        if show:
            fig.show()
        
        return fig
    
    def plot_returns_distribution(self, show: bool = True, save_path: str = None):
        equity_curve = self.results.get('equity_curve', [])
        
        if len(equity_curve) < 2:
            print("Insufficient data for returns distribution")
            return
        
        values = [point['value'] for point in equity_curve]
        returns = pd.Series(values).pct_change().dropna() * 100
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=returns,
            nbinsx=50,
            name='Returns',
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title='Returns Distribution',
            xaxis_title='Return (%)',
            yaxis_title='Frequency',
            template='plotly_white'
        )
        
        if save_path:
            fig.write_html(save_path)
        
        if show:
            fig.show()
        
        return fig
    
    def plot_trades(self, symbol: str = None, show: bool = True, save_path: str = None):
        trades = self.results.get('trades', [])
        
        if not trades:
            print("No trades available")
            return
        
        if symbol:
            trades = [t for t in trades if t.symbol == symbol]
        
        buy_trades = [t for t in trades if t.side.upper() == "BUY"]
        sell_trades = [t for t in trades if t.side.upper() == "SELL"]
        
        fig = go.Figure()
        
        if buy_trades:
            fig.add_trace(go.Scatter(
                x=[t.timestamp for t in buy_trades],
                y=[t.price for t in buy_trades],
                mode='markers',
                name='Buy',
                marker=dict(color='green', size=10, symbol='triangle-up')
            ))
        
        if sell_trades:
            fig.add_trace(go.Scatter(
                x=[t.timestamp for t in sell_trades],
                y=[t.price for t in sell_trades],
                mode='markers',
                name='Sell',
                marker=dict(color='red', size=10, symbol='triangle-down')
            ))
        
        title = f'Trade Execution Points{" for " + symbol if symbol else ""}'
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Price ($)',
            hovermode='closest',
            template='plotly_white'
        )
        
        if save_path:
            fig.write_html(save_path)
        
        if show:
            fig.show()
        
        return fig
    
    def generate_report(self, save_path: str = None):
        report = []
        report.append("="*80)
        report.append("BACKTEST PERFORMANCE REPORT")
        report.append("="*80)
        report.append("")
        
        report.append("Performance Metrics:")
        report.append(f"  Total Return: {self.results.get('total_return_pct', 0):.2f}%")
        report.append(f"  Sharpe Ratio: {self.results.get('sharpe_ratio', 0):.3f}")
        report.append(f"  Sortino Ratio: {self.results.get('sortino_ratio', 0):.3f}")
        report.append(f"  Max Drawdown: {self.results.get('max_drawdown_pct', 0):.2f}%")
        report.append("")
        
        report.append("Trading Statistics:")
        report.append(f"  Total Trades: {self.results.get('total_trades', 0)}")
        report.append(f"  Win Rate: {self.results.get('win_rate', 0):.2%}")
        report.append(f"  Profit Factor: {self.results.get('profit_factor', 0):.2f}")
        report.append("")
        
        report.append("="*80)
        
        report_text = "\n".join(report)
        
        if save_path:
            with open(save_path, 'w') as f:
                f.write(report_text)
        
        print(report_text)
        
        return report_text
