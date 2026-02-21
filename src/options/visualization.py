"""Visualization utilities for options payoff and Greeks.

This module provides classes for plotting option payoffs, Greeks sensitivity analysis,
and strategy comparisons using both matplotlib (static) and plotly (interactive).
"""

from typing import Optional, Union, List, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.options.payoff import (
    OptionPosition, Strategy, OptionType, OptionSide,
    create_long_call, create_long_put
)
from src.options.greeks import (
    Greeks, GreeksCalculator, StrategyGreeks,
    delta, gamma, theta, vega, rho, black_scholes_price
)


class PayoffPlotter:
    """Plotter for option payoff diagrams."""
    
    def __init__(self, use_plotly: bool = True):
        """Initialize the plotter.
        
        Args:
            use_plotly: If True, use plotly for interactive plots;
                       if False, use matplotlib for static plots.
        """
        self.use_plotly = use_plotly
    
    def plot_payoff(
        self,
        strategy: Strategy,
        min_price: float,
        max_price: float,
        num_points: int = 100,
        title: Optional[str] = None,
        show: bool = True,
        save_path: Optional[str] = None
    ) -> Union[go.Figure, plt.Figure]:
        """Plot the payoff diagram for a strategy.
        
        Args:
            strategy: The option strategy to plot.
            min_price: Minimum underlying price to plot.
            max_price: Maximum underlying price to plot.
            num_points: Number of price points.
            title: Optional plot title.
            show: Whether to display the plot.
            save_path: Optional path to save the figure.
            
        Returns:
            The figure object (plotly or matplotlib).
        """
        prices = np.linspace(min_price, max_price, num_points)
        
        if self.use_plotly:
            return self._plot_payoff_plotly(
                strategy, prices, title, show, save_path
            )
        else:
            return self._plot_payoff_mpl(
                strategy, prices, title, show, save_path
            )
    
    def _plot_payoff_plotly(
        self,
        strategy: Strategy,
        prices: np.ndarray,
        title: Optional[str],
        show: bool,
        save_path: Optional[str]
    ) -> go.Figure:
        """Create payoff plot using plotly."""
        fig = go.Figure()
        
        # Add individual position payoffs
        colors = ['blue', 'green', 'red', 'orange', 'purple', 'cyan']
        for i, pos in enumerate(strategy.positions):
            payoff = pos.payoff_at_expiration(prices)
            fig.add_trace(go.Scatter(
                x=prices,
                y=payoff,
                mode='lines',
                name=f'Leg {i+1}: {pos.option_type.value} @ ${pos.strike:.2f}',
                line=dict(color=colors[i % len(colors)], width=1, dash='dash'),
                opacity=0.6
            ))
        
        # Add total payoff
        total = strategy.total_payoff(prices)
        fig.add_trace(go.Scatter(
            x=prices,
            y=total,
            mode='lines',
            name='Total Payoff',
            line=dict(color='black', width=3)
        ))
        
        # Add breakeven line
        fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title=title or f'{strategy.name} - Payoff at Expiration',
            xaxis_title='Underlying Price at Expiration ($)',
            yaxis_title='Profit / Loss ($)',
            hovermode='x unified',
            template='plotly_white',
            showlegend=True
        )
        
        if save_path:
            fig.write_html(save_path)
        
        if show:
            fig.show()
        
        return fig
    
    def _plot_payoff_mpl(
        self,
        strategy: Strategy,
        prices: np.ndarray,
        title: Optional[str],
        show: bool,
        save_path: Optional[str]
    ) -> plt.Figure:
        """Create payoff plot using matplotlib."""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Add individual position payoffs
        for i, pos in enumerate(strategy.positions):
            payoff = pos.payoff_at_expiration(prices)
            ax.plot(prices, payoff, '--', alpha=0.5,
                   label=f'Leg {i+1}: {pos.option_type.value} @ ${pos.strike:.2f}')
        
        # Add total payoff
        total = strategy.total_payoff(prices)
        ax.plot(prices, total, 'k-', linewidth=2.5, label='Total Payoff')
        
        # Add breakeven line
        ax.axhline(y=0, color='gray', linestyle=':', alpha=0.5)
        
        # Fill profit/loss regions
        ax.fill_between(prices, 0, total, where=(total >= 0),
                        alpha=0.2, color='green', label='Profit Zone')
        ax.fill_between(prices, 0, total, where=(total < 0),
                        alpha=0.2, color='red', label='Loss Zone')
        
        ax.set_xlabel('Underlying Price at Expiration ($)', fontsize=12)
        ax.set_ylabel('Profit / Loss ($)', fontsize=12)
        ax.set_title(title or f'{strategy.name} - Payoff at Expiration', fontsize=14)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        if show:
            plt.show()
        
        return fig
    
    def plot_multiple_strategies(
        self,
        strategies: List[Strategy],
        min_price: float,
        max_price: float,
        num_points: int = 100,
        title: Optional[str] = None,
        show: bool = True,
        save_path: Optional[str] = None
    ) -> Union[go.Figure, plt.Figure]:
        """Plot multiple strategies for comparison.
        
        Args:
            strategies: List of strategies to compare.
            min_price: Minimum underlying price.
            max_price: Maximum underlying price.
            num_points: Number of price points.
            title: Optional plot title.
            show: Whether to display the plot.
            save_path: Optional path to save.
            
        Returns:
            The figure object.
        """
        prices = np.linspace(min_price, max_price, num_points)
        
        if self.use_plotly:
            fig = go.Figure()
            colors = ['blue', 'green', 'red', 'orange', 'purple']
            
            for i, strategy in enumerate(strategies):
                total = strategy.total_payoff(prices)
                fig.add_trace(go.Scatter(
                    x=prices,
                    y=total,
                    mode='lines',
                    name=strategy.name,
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
            
            fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5)
            
            fig.update_layout(
                title=title or 'Strategy Comparison',
                xaxis_title='Underlying Price at Expiration ($)',
                yaxis_title='Profit / Loss ($)',
                hovermode='x unified',
                template='plotly_white'
            )
            
            if save_path:
                fig.write_html(save_path)
            if show:
                fig.show()
            return fig
        else:
            fig, ax = plt.subplots(figsize=(12, 7))
            
            for strategy in strategies:
                total = strategy.total_payoff(prices)
                ax.plot(prices, total, linewidth=2, label=strategy.name)
            
            ax.axhline(y=0, color='gray', linestyle=':', alpha=0.5)
            ax.set_xlabel('Underlying Price at Expiration ($)')
            ax.set_ylabel('Profit / Loss ($)')
            ax.set_title(title or 'Strategy Comparison')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
            if show:
                plt.show()
            return fig


class GreeksPlotter:
    """Plotter for Greeks visualization."""
    
    def __init__(self, use_plotly: bool = True):
        """Initialize the plotter.
        
        Args:
            use_plotly: If True, use plotly; otherwise matplotlib.
        """
        self.use_plotly = use_plotly
    
    def plot_greeks_vs_price(
        self,
        position: OptionPosition,
        min_price: float,
        max_price: float,
        time_to_expiry: float,
        volatility: float,
        risk_free_rate: float = 0.02,
        num_points: int = 100,
        greeks_to_plot: Optional[List[str]] = None,
        show: bool = True,
        save_path: Optional[str] = None
    ) -> Union[go.Figure, plt.Figure]:
        """Plot Greeks as a function of underlying price.
        
        Args:
            position: The option position.
            min_price: Minimum underlying price.
            max_price: Maximum underlying price.
            time_to_expiry: Time to expiration in years.
            volatility: Annualized volatility.
            risk_free_rate: Annual risk-free rate.
            num_points: Number of price points.
            greeks_to_plot: List of Greeks to plot (default: all).
            show: Whether to display.
            save_path: Optional save path.
            
        Returns:
            The figure object.
        """
        prices = np.linspace(min_price, max_price, num_points)
        greeks_list = greeks_to_plot or ['delta', 'gamma', 'theta', 'vega', 'rho']
        
        # Calculate Greeks
        greeks_data = {}
        if 'delta' in greeks_list:
            greeks_data['delta'] = delta(
                prices, position.strike, time_to_expiry,
                risk_free_rate, volatility, position.option_type
            )
        if 'gamma' in greeks_list:
            greeks_data['gamma'] = gamma(
                prices, position.strike, time_to_expiry, risk_free_rate, volatility
            )
        if 'theta' in greeks_list:
            greeks_data['theta'] = theta(
                prices, position.strike, time_to_expiry,
                risk_free_rate, volatility, position.option_type
            ) / 365  # Convert to daily
        if 'vega' in greeks_list:
            greeks_data['vega'] = vega(
                prices, position.strike, time_to_expiry, risk_free_rate, volatility
            )
        if 'rho' in greeks_list:
            greeks_data['rho'] = rho(
                prices, position.strike, time_to_expiry,
                risk_free_rate, volatility, position.option_type
            )
        
        if self.use_plotly:
            return self._plot_greeks_plotly(prices, greeks_data, position, show, save_path)
        else:
            return self._plot_greeks_mpl(prices, greeks_data, position, show, save_path)
    
    def _plot_greeks_plotly(
        self,
        prices: np.ndarray,
        greeks_data: dict,
        position: OptionPosition,
        show: bool,
        save_path: Optional[str]
    ) -> go.Figure:
        """Plot Greeks using plotly with subplots."""
        n_greeks = len(greeks_data)
        fig = make_subplots(
            rows=n_greeks, cols=1,
            subplot_titles=list(greeks_data.keys()),
            vertical_spacing=0.08
        )
        
        colors = {'delta': 'blue', 'gamma': 'green', 'theta': 'red',
                  'vega': 'purple', 'rho': 'orange'}
        
        for i, (greek_name, values) in enumerate(greeks_data.items(), 1):
            fig.add_trace(go.Scatter(
                x=prices,
                y=values,
                mode='lines',
                name=greek_name.capitalize(),
                line=dict(color=colors.get(greek_name, 'blue')),
                showlegend=False
            ), row=i, col=1)
            
            # Add strike line
            fig.add_vline(
                x=position.strike,
                line_dash="dash",
                line_color="gray",
                opacity=0.5,
                row=i, col=1
            )
        
        fig.update_layout(
            title=f'Greeks Analysis - {position.option_type.value.capitalize()} @ ${position.strike:.2f}',
            hovermode='x unified',
            template='plotly_white',
            height=200 * n_greeks
        )
        
        if save_path:
            fig.write_html(save_path)
        if show:
            fig.show()
        return fig
    
    def _plot_greeks_mpl(
        self,
        prices: np.ndarray,
        greeks_data: dict,
        position: OptionPosition,
        show: bool,
        save_path: Optional[str]
    ) -> plt.Figure:
        """Plot Greeks using matplotlib with subplots."""
        n_greeks = len(greeks_data)
        fig, axes = plt.subplots(n_greeks, 1, figsize=(12, 3 * n_greeks), sharex=True)
        
        if n_greeks == 1:
            axes = [axes]
        
        colors = {'delta': 'blue', 'gamma': 'green', 'theta': 'red',
                  'vega': 'purple', 'rho': 'orange'}
        
        for ax, (greek_name, values) in zip(axes, greeks_data.items()):
            ax.plot(prices, values, color=colors.get(greek_name, 'blue'), linewidth=2)
            ax.axvline(x=position.strike, color='gray', linestyle='--', alpha=0.5)
            ax.set_ylabel(greek_name.capitalize(), fontsize=11)
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='gray', linestyle=':', alpha=0.3)
        
        axes[-1].set_xlabel('Underlying Price ($)', fontsize=12)
        fig.suptitle(f'Greeks Analysis - {position.option_type.value.capitalize()} @ ${position.strike:.2f}',
                     fontsize=14)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        if show:
            plt.show()
        return fig
    
    def plot_greeks_vs_time(
        self,
        position: OptionPosition,
        spot: float,
        max_time: float,
        volatility: float,
        risk_free_rate: float = 0.02,
        num_points: int = 50,
        greeks_to_plot: Optional[List[str]] = None,
        show: bool = True,
        save_path: Optional[str] = None
    ) -> Union[go.Figure, plt.Figure]:
        """Plot Greeks as a function of time to expiration.
        
        Args:
            position: The option position.
            spot: Current underlying price.
            max_time: Maximum time to expiration in years.
            volatility: Annualized volatility.
            risk_free_rate: Annual risk-free rate.
            num_points: Number of time points.
            greeks_to_plot: List of Greeks to plot.
            show: Whether to display.
            save_path: Optional save path.
            
        Returns:
            The figure object.
        """
        times = np.linspace(0.001, max_time, num_points)
        greeks_list = greeks_to_plot or ['delta', 'gamma', 'theta', 'vega', 'rho']
        
        greeks_data = {}
        if 'delta' in greeks_list:
            greeks_data['delta'] = [delta(
                spot, position.strike, t, risk_free_rate, volatility, position.option_type
            ) for t in times]
        if 'gamma' in greeks_list:
            greeks_data['gamma'] = [gamma(
                spot, position.strike, t, risk_free_rate, volatility
            ) for t in times]
        if 'theta' in greeks_list:
            greeks_data['theta'] = [theta(
                spot, position.strike, t, risk_free_rate, volatility, position.option_type
            ) / 365 for t in times]
        if 'vega' in greeks_list:
            greeks_data['vega'] = [vega(
                spot, position.strike, t, risk_free_rate, volatility
            ) for t in times]
        if 'rho' in greeks_list:
            greeks_data['rho'] = [rho(
                spot, position.strike, t, risk_free_rate, volatility, position.option_type
            ) for t in times]
        
        if self.use_plotly:
            fig = make_subplots(
                rows=len(greeks_data), cols=1,
                subplot_titles=list(greeks_data.keys()),
                vertical_spacing=0.08
            )
            
            colors = {'delta': 'blue', 'gamma': 'green', 'theta': 'red',
                      'vega': 'purple', 'rho': 'orange'}
            
            for i, (greek_name, values) in enumerate(greeks_data.items(), 1):
                fig.add_trace(go.Scatter(
                    x=times * 365,  # Convert to days
                    y=values,
                    mode='lines',
                    name=greek_name.capitalize(),
                    line=dict(color=colors.get(greek_name, 'blue')),
                    showlegend=False
                ), row=i, col=1)
            
            fig.update_layout(
                title=f'Time Decay Analysis - {position.option_type.value.capitalize()} @ ${position.strike:.2f}',
                hovermode='x unified',
                template='plotly_white',
                height=200 * len(greeks_data)
            )
            
            if save_path:
                fig.write_html(save_path)
            if show:
                fig.show()
            return fig
        else:
            n_greeks = len(greeks_data)
            fig, axes = plt.subplots(n_greeks, 1, figsize=(12, 3 * n_greeks), sharex=True)
            
            if n_greeks == 1:
                axes = [axes]
            
            colors = {'delta': 'blue', 'gamma': 'green', 'theta': 'red',
                      'vega': 'purple', 'rho': 'orange'}
            
            for ax, (greek_name, values) in zip(axes, greeks_data.items()):
                ax.plot(times * 365, values, color=colors.get(greek_name, 'blue'), linewidth=2)
                ax.set_ylabel(greek_name.capitalize(), fontsize=11)
                ax.grid(True, alpha=0.3)
            
            axes[-1].set_xlabel('Days to Expiration', fontsize=12)
            fig.suptitle(f'Time Decay Analysis - {position.option_type.value.capitalize()} @ ${position.strike:.2f}',
                         fontsize=14)
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
            if show:
                plt.show()
            return fig


class StrategyPlotter:
    """Combined plotter for strategy payoffs and Greeks."""
    
    def __init__(self, use_plotly: bool = True):
        """Initialize the plotter.
        
        Args:
            use_plotly: If True, use plotly; otherwise matplotlib.
        """
        self.use_plotly = use_plotly
        self.payoff_plotter = PayoffPlotter(use_plotly)
        self.greeks_plotter = GreeksPlotter(use_plotly)
    
    def plot_strategy_analysis(
        self,
        strategy: Strategy,
        spot: float,
        min_price: float,
        max_price: float,
        time_to_expiry: float,
        volatility: float,
        risk_free_rate: float = 0.02,
        num_points: int = 100,
        show: bool = True,
        save_path: Optional[str] = None
    ) -> Union[go.Figure, plt.Figure]:
        """Create a comprehensive strategy analysis plot.
        
        Shows payoff at expiration and aggregated Greeks vs price.
        
        Args:
            strategy: The option strategy.
            spot: Current underlying price.
            min_price: Minimum price for analysis.
            max_price: Maximum price for analysis.
            time_to_expiry: Time to expiration in years.
            volatility: Annualized volatility.
            risk_free_rate: Annual risk-free rate.
            num_points: Number of price points.
            show: Whether to display.
            save_path: Optional save path.
            
        Returns:
            The figure object.
        """
        if self.use_plotly:
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=('Payoff at Expiration', 'Delta',
                               'Gamma', 'Theta (Daily)',
                               'Vega', 'Strategy Info'),
                specs=[[{"type": "scatter"}, {"type": "scatter"}],
                       [{"type": "scatter"}, {"type": "scatter"}],
                       [{"type": "scatter"}, {"type": "table"}]]
            )
            
            prices = np.linspace(min_price, max_price, num_points)
            
            # Payoff
            payoff = strategy.total_payoff(prices)
            fig.add_trace(go.Scatter(
                x=prices, y=payoff, mode='lines',
                name='Payoff', line=dict(color='black', width=2),
                showlegend=False
            ), row=1, col=1)
            fig.add_hline(y=0, line_dash="dot", line_color="gray", row=1, col=1)
            
            # Calculate aggregated Greeks
            calc = GreeksCalculator(risk_free_rate=risk_free_rate, volatility=volatility)
            
            deltas, gammas, thetas, vegas, rhos = [], [], [], [], []
            for price in prices:
                greeks = []
                for pos in strategy.positions:
                    g = calc.calculate_for_position(pos, price, time_to_expiry)
                    greeks.append(g)
                
                deltas.append(sum(g.delta for g in greeks))
                gammas.append(sum(g.gamma for g in greeks))
                thetas.append(sum(g.theta for g in greeks) / 365)
                vegas.append(sum(g.vega for g in greeks))
                rhos.append(sum(g.rho for g in greeks))
            
            # Greeks plots
            fig.add_trace(go.Scatter(x=prices, y=deltas, mode='lines',
                           name='Delta', line=dict(color='blue'), showlegend=False), row=1, col=2)
            fig.add_trace(go.Scatter(x=prices, y=gammas, mode='lines',
                           name='Gamma', line=dict(color='green'), showlegend=False), row=2, col=1)
            fig.add_trace(go.Scatter(x=prices, y=thetas, mode='lines',
                           name='Theta', line=dict(color='red'), showlegend=False), row=2, col=2)
            fig.add_trace(go.Scatter(x=prices, y=vegas, mode='lines',
                           name='Vega', line=dict(color='purple'), showlegend=False), row=3, col=1)
            
            # Strategy info table
            net_premium = strategy.net_premium()
            breakevens = strategy.calculate_breakevens(min_price, max_price)
            
            fig.add_trace(go.Table(
                header=dict(values=['Metric', 'Value']),
                cells=dict(values=[
                    ['Strategy', 'Net Premium', 'Breakevens', 'Current Spot'],
                    [strategy.name, f'${net_premium:,.2f}',
                     ', '.join(f'${b:.2f}' for b in breakevens) if breakevens else 'N/A',
                     f'${spot:.2f}']
                ])
            ), row=3, col=2)
            
            fig.update_layout(
                title=f'{strategy.name} - Comprehensive Analysis',
                template='plotly_white',
                height=800
            )
            
            if save_path:
                fig.write_html(save_path)
            if show:
                fig.show()
            return fig
        else:
            # Matplotlib version
            fig = plt.figure(figsize=(14, 10))
            gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
            
            prices = np.linspace(min_price, max_price, num_points)
            
            # Payoff
            ax1 = fig.add_subplot(gs[0, 0])
            payoff = strategy.total_payoff(prices)
            ax1.plot(prices, payoff, 'k-', linewidth=2)
            ax1.axhline(y=0, color='gray', linestyle=':')
            ax1.set_title('Payoff at Expiration')
            ax1.set_ylabel('P/L ($)')
            ax1.grid(True, alpha=0.3)
            
            # Calculate Greeks
            calc = GreeksCalculator(risk_free_rate=risk_free_rate, volatility=volatility)
            
            deltas, gammas, thetas, vegas = [], [], [], []
            for price in prices:
                greeks = []
                for pos in strategy.positions:
                    g = calc.calculate_for_position(pos, price, time_to_expiry)
                    greeks.append(g)
                deltas.append(sum(g.delta for g in greeks))
                gammas.append(sum(g.gamma for g in greeks))
                thetas.append(sum(g.theta for g in greeks) / 365)
                vegas.append(sum(g.vega for g in greeks))
            
            # Delta
            ax2 = fig.add_subplot(gs[0, 1])
            ax2.plot(prices, deltas, 'b-', linewidth=2)
            ax2.set_title('Delta')
            ax2.grid(True, alpha=0.3)
            
            # Gamma
            ax3 = fig.add_subplot(gs[1, 0])
            ax3.plot(prices, gammas, 'g-', linewidth=2)
            ax3.set_title('Gamma')
            ax3.grid(True, alpha=0.3)
            
            # Theta
            ax4 = fig.add_subplot(gs[1, 1])
            ax4.plot(prices, thetas, 'r-', linewidth=2)
            ax4.set_title('Theta (Daily)')
            ax4.grid(True, alpha=0.3)
            
            # Vega
            ax5 = fig.add_subplot(gs[2, 0])
            ax5.plot(prices, vegas, 'purple', linewidth=2)
            ax5.set_title('Vega')
            ax5.set_xlabel('Underlying Price ($)')
            ax5.grid(True, alpha=0.3)
            
            # Info text
            ax6 = fig.add_subplot(gs[2, 1])
            ax6.axis('off')
            net_premium = strategy.net_premium()
            breakevens = strategy.calculate_breakevens(min_price, max_price)
            info_text = f"""
            Strategy: {strategy.name}
            Net Premium: ${net_premium:,.2f}
            Breakevens: {', '.join(f'${b:.2f}' for b in breakevens) if breakevens else 'N/A'}
            Current Spot: ${spot:.2f}
            Time to Expiry: {time_to_expiry:.4f} years
            Volatility: {volatility:.1%}
            """
            ax6.text(0.1, 0.5, info_text, fontsize=11, verticalalignment='center',
                    family='monospace')
            
            fig.suptitle(f'{strategy.name} - Comprehensive Analysis', fontsize=14)
            
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
            if show:
                plt.show()
            return fig
