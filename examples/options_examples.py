#!/usr/bin/env python3
"""Examples demonstrating the options analytics module.

This script demonstrates various features of the options module including:
- Single option payoff calculations
- Multi-leg strategy construction
- Greeks calculations
- Visualization
"""

import numpy as np
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.options import (
    OptionType, OptionSide, OptionPosition, Strategy,
    create_long_call, create_long_put,
    create_long_straddle, create_short_straddle,
    create_long_strangle, create_bull_call_spread,
    create_bear_put_spread, create_long_butterfly, create_iron_condor,
    GreeksCalculator, StrategyGreeks,
    PayoffPlotter, GreeksPlotter, StrategyPlotter
)


def example_1_single_option():
    """Example 1: Single option payoff calculation."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Single Option Payoff")
    print("="*60)
    
    # Create a long call option
    call = create_long_call(strike=100, premium=5.00)
    print(f"\nPosition: {call}")
    
    # Calculate payoff at different underlying prices
    prices = [90, 95, 100, 105, 110]
    print("\nPayoff at expiration:")
    for price in prices:
        payoff = call.payoff_at_expiration(price)
        print(f"  Spot=${price}: Payoff=${payoff:.2f}")
    
    # Max profit/loss
    print(f"\nMax Profit: {'Unlimited' if call.max_profit() is None else f'${call.max_profit():.2f}'}")
    print(f"Max Loss: ${call.max_loss():.2f}")


def example_2_strategy_construction():
    """Example 2: Multi-leg strategy construction."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Multi-Leg Strategy Construction")
    print("="*60)
    
    # Create a long straddle
    straddle = create_long_straddle(
        strike=100,
        premium_call=3.00,
        premium_put=2.50
    )
    
    print(f"\nStrategy: {straddle.name}")
    print(f"Number of legs: {len(straddle.positions)}")
    print(f"Net Premium Paid: ${abs(straddle.net_premium()):.2f}")
    
    # Payoff matrix
    matrix = straddle.payoff_matrix(min_price=80, max_price=120, num_points=5)
    print("\nPayoff Matrix:")
    print(matrix.to_string(index=False))
    
    # Breakeven points
    breakevens = straddle.calculate_breakevens(80, 120)
    print(f"\nBreakeven Points: {[f'${b:.2f}' for b in breakevens]}")
    
    # Max profit/loss
    max_profit, max_loss = straddle.max_profit_loss(80, 120)
    print(f"Max Profit: {'Unlimited' if max_profit is None else f'${max_profit:.2f}'}")
    print(f"Max Loss: ${max_loss:.2f}")


def example_3_greeks_calculation():
    """Example 3: Greeks calculation using Black-Scholes."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Greeks Calculation")
    print("="*60)
    
    # Create Greeks calculator
    calc = GreeksCalculator(risk_free_rate=0.05, volatility=0.20)
    
    # Calculate Greeks for a call option
    call = create_long_call(strike=100, premium=5.00)
    greeks = calc.calculate_for_position(
        position=call,
        spot=100,
        time_to_expiry=30/365  # 30 days
    )
    
    print(f"\nPosition: {call}")
    print(f"Spot Price: ${greeks.spot}")
    print(f"Time to Expiry: {greeks.time_to_expiry:.4f} years ({greeks.time_to_expiry*365:.0f} days)")
    print(f"Volatility: {greeks.volatility:.1%}")
    print(f"Risk-Free Rate: {greeks.risk_free_rate:.1%}")
    
    print(f"\nGreeks:")
    print(f"  Delta:  {greeks.delta:+.4f}")
    print(f"  Gamma:  {greeks.gamma:.4f}")
    print(f"  Theta:  {greeks.theta:.4f} (annual)")
    print(f"  Theta:  {greeks.theta/365:.4f} (daily)")
    print(f"  Vega:   {greeks.vega:.4f} (per 1% vol)")
    print(f"  Rho:    {greeks.rho:.4f} (per 1% rate)")
    
    # Strategy Greeks
    print("\n--- Strategy Greeks Example ---")
    straddle = create_long_straddle(strike=100, premium_call=3.00, premium_put=2.50)
    strategy_greeks = StrategyGreeks(straddle)
    agg_greeks = strategy_greeks.calculate(
        spot=100,
        time_to_expiry=30/365,
        volatility=0.20,
        risk_free_rate=0.05
    )
    
    print(f"\nStrategy: {straddle.name}")
    print(f"Aggregated Greeks:")
    print(f"  Delta:  {agg_greeks.delta:+.4f}")
    print(f"  Gamma:  {agg_greeks.gamma:.4f}")
    print(f"  Theta:  {agg_greeks.theta/365:.4f} (daily)")
    print(f"  Vega:   {agg_greeks.vega:.4f}")


def example_4_common_strategies():
    """Example 4: Common options strategies."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Common Options Strategies")
    print("="*60)
    
    strategies = [
        ("Long Straddle", create_long_straddle(100, 3.00, 2.50)),
        ("Short Straddle", create_short_straddle(100, 3.00, 2.50)),
        ("Bull Call Spread", create_bull_call_spread(95, 105, 5.00, 2.00)),
        ("Bear Put Spread", create_bear_put_spread(95, 105, 1.50, 4.50)),
        ("Long Butterfly", create_long_butterfly(100, 10, 1.00, 3.00, 1.00)),
    ]
    
    for name, strategy in strategies:
        print(f"\n{name}:")
        print(f"  Net Premium: ${strategy.net_premium():+.2f}")
        
        breakevens = strategy.calculate_breakevens(80, 120)
        print(f"  Breakevens: {[f'${b:.2f}' for b in breakevens]}")
        
        max_p, max_l = strategy.max_profit_loss(80, 120)
        profit_str = 'Unlimited' if max_p is None else f'${max_p:.2f}'
        loss_str = 'Unlimited' if max_l is None else f'${max_l:.2f}'
        print(f"  Max Profit: {profit_str}")
        print(f"  Max Loss: {loss_str}")


def example_5_payoff_visualization():
    """Example 5: Visualizing option payoffs."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Payoff Visualization")
    print("="*60)
    
    # Create a straddle strategy
    straddle = create_long_straddle(strike=100, premium_call=3.00, premium_put=2.50)
    
    # Create plotter
    plotter = PayoffPlotter(use_plotly=False)  # Use matplotlib for examples
    
    print("\nGenerating payoff plot...")
    fig = plotter.plot_payoff(
        strategy=straddle,
        min_price=80,
        max_price=120,
        title="Long Straddle Payoff",
        show=False
    )
    
    # Save the plot
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, 'straddle_payoff.png')
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"  Saved to: {save_path}")
    plt.close(fig)
    
    # Strategy comparison
    print("\nGenerating strategy comparison plot...")
    strangle = create_long_strangle(95, 105, 1.50, 1.50)
    spread = create_bull_call_spread(95, 105, 5.00, 2.00)
    
    fig = plotter.plot_multiple_strategies(
        strategies=[straddle, strangle, spread],
        min_price=80,
        max_price=120,
        title="Strategy Comparison",
        show=False
    )
    save_path = os.path.join(output_dir, 'strategy_comparison.png')
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"  Saved to: {save_path}")
    plt.close(fig)


def example_6_greeks_visualization():
    """Example 6: Visualizing Greeks."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Greeks Visualization")
    print("="*60)
    
    # Create a call option
    call = create_long_call(strike=100, premium=5.00)
    
    # Create plotter
    plotter = GreeksPlotter(use_plotly=False)
    
    print("\nGenerating Greeks vs Price plot...")
    fig = plotter.plot_greeks_vs_price(
        position=call,
        min_price=80,
        max_price=120,
        time_to_expiry=30/365,
        volatility=0.20,
        risk_free_rate=0.05,
        show=False
    )
    
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, 'greeks_vs_price.png')
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"  Saved to: {save_path}")
    plt.close(fig)
    
    print("\nGenerating Greeks vs Time plot...")
    fig = plotter.plot_greeks_vs_time(
        position=call,
        spot=100,
        max_time=90/365,  # 90 days
        volatility=0.20,
        risk_free_rate=0.05,
        show=False
    )
    save_path = os.path.join(output_dir, 'greeks_vs_time.png')
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"  Saved to: {save_path}")
    plt.close(fig)


def example_7_comprehensive_analysis():
    """Example 7: Comprehensive strategy analysis."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Comprehensive Strategy Analysis")
    print("="*60)
    
    # Create an iron condor
    condor = create_iron_condor(
        strike_put_low=90,
        strike_put_high=95,
        strike_call_low=105,
        strike_call_high=110,
        premium_put_low=0.50,
        premium_put_high=2.00,
        premium_call_low=2.00,
        premium_call_high=0.50
    )
    
    print(f"\nStrategy: {condor.name}")
    print(f"Net Premium Received: ${abs(condor.net_premium()):.2f}")
    
    # Create comprehensive plot
    plotter = StrategyPlotter(use_plotly=False)
    
    print("\nGenerating comprehensive analysis plot...")
    fig = plotter.plot_strategy_analysis(
        strategy=condor,
        spot=100,
        min_price=80,
        max_price=120,
        time_to_expiry=30/365,
        volatility=0.20,
        risk_free_rate=0.05,
        show=False
    )
    
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, 'comprehensive_analysis.png')
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"  Saved to: {save_path}")
    plt.close(fig)


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("OPTIONS ANALYTICS MODULE - EXAMPLES")
    print("="*60)
    
    example_1_single_option()
    example_2_strategy_construction()
    example_3_greeks_calculation()
    example_4_common_strategies()
    
    # Visualization examples (require matplotlib)
    try:
        import matplotlib
        example_5_payoff_visualization()
        example_6_greeks_visualization()
        example_7_comprehensive_analysis()
    except ImportError:
        print("\nMatplotlib not available, skipping visualization examples.")
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60 + "\n")


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    main()
