"""Tests for options visualization functionality."""

import pytest
import numpy as np
import os
import tempfile

from src.options.visualization import (
    PayoffPlotter, GreeksPlotter, StrategyPlotter
)
from src.options.payoff import (
    create_long_call, create_long_put,
    create_long_straddle, create_bull_call_spread,
    create_iron_condor
)
from src.options.greeks import GreeksCalculator

# Skip matplotlib tests if not available
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


class TestPayoffPlotter:
    """Tests for PayoffPlotter class."""
    
    @pytest.mark.skipif(not HAS_MATPLOTLIB, reason="Matplotlib not available")
    def test_plot_payoff_matplotlib(self):
        """Should create matplotlib figure."""
        plotter = PayoffPlotter(use_plotly=False)
        straddle = create_long_straddle(100, 3.00, 2.50)
        
        fig = plotter.plot_payoff(
            strategy=straddle,
            min_price=80, max_price=120,
            show=False
        )
        
        assert fig is not None
        plt.close(fig)
    
    @pytest.mark.skipif(not HAS_PLOTLY, reason="Plotly not available")
    def test_plot_payoff_plotly(self):
        """Should create plotly figure."""
        plotter = PayoffPlotter(use_plotly=True)
        straddle = create_long_straddle(100, 3.00, 2.50)
        
        fig = plotter.plot_payoff(
            strategy=straddle,
            min_price=80, max_price=120,
            show=False
        )
        
        assert fig is not None
        assert isinstance(fig, go.Figure)
    
    @pytest.mark.skipif(not HAS_MATPLOTLIB, reason="Matplotlib not available")
    def test_plot_payoff_save(self):
        """Should save figure to file."""
        plotter = PayoffPlotter(use_plotly=False)
        straddle = create_long_straddle(100, 3.00, 2.50)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        try:
            fig = plotter.plot_payoff(
                strategy=straddle,
                min_price=80, max_price=120,
                show=False,
                save_path=temp_path
            )
            plt.close(fig)
            
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @pytest.mark.skipif(not HAS_MATPLOTLIB, reason="Matplotlib not available")
    def test_plot_multiple_strategies(self):
        """Should plot multiple strategies for comparison."""
        plotter = PayoffPlotter(use_plotly=False)
        
        strategies = [
            create_long_straddle(100, 3.00, 2.50),
            create_bull_call_spread(95, 105, 5.00, 2.00)
        ]
        
        fig = plotter.plot_multiple_strategies(
            strategies=strategies,
            min_price=80, max_price=120,
            show=False
        )
        
        assert fig is not None
        plt.close(fig)
    
    def test_custom_title(self):
        """Should use custom title when provided."""
        plotter = PayoffPlotter(use_plotly=False)
        straddle = create_long_straddle(100, 3.00, 2.50)
        
        custom_title = "My Custom Title"
        fig = plotter.plot_payoff(
            strategy=straddle,
            min_price=80, max_price=120,
            title=custom_title,
            show=False
        )
        
        assert fig is not None
        plt.close(fig)


class TestGreeksPlotter:
    """Tests for GreeksPlotter class."""
    
    @pytest.mark.skipif(not HAS_MATPLOTLIB, reason="Matplotlib not available")
    def test_plot_greeks_vs_price(self):
        """Should plot Greeks vs underlying price."""
        plotter = GreeksPlotter(use_plotly=False)
        call = create_long_call(100, 5.00)
        
        fig = plotter.plot_greeks_vs_price(
            position=call,
            min_price=80, max_price=120,
            time_to_expiry=0.25,
            volatility=0.20,
            risk_free_rate=0.05,
            show=False
        )
        
        assert fig is not None
        plt.close(fig)
    
    @pytest.mark.skipif(not HAS_MATPLOTLIB, reason="Matplotlib not available")
    def test_plot_greeks_vs_time(self):
        """Should plot Greeks vs time to expiration."""
        plotter = GreeksPlotter(use_plotly=False)
        call = create_long_call(100, 5.00)
        
        fig = plotter.plot_greeks_vs_time(
            position=call,
            spot=100,
            max_time=0.25,
            volatility=0.20,
            risk_free_rate=0.05,
            show=False
        )
        
        assert fig is not None
        plt.close(fig)
    
    @pytest.mark.skipif(not HAS_MATPLOTLIB, reason="Matplotlib not available")
    def test_plot_subset_of_greeks(self):
        """Should be able to plot subset of Greeks."""
        plotter = GreeksPlotter(use_plotly=False)
        call = create_long_call(100, 5.00)
        
        fig = plotter.plot_greeks_vs_price(
            position=call,
            min_price=80, max_price=120,
            time_to_expiry=0.25,
            volatility=0.20,
            greeks_to_plot=['delta', 'gamma'],
            show=False
        )
        
        assert fig is not None
        plt.close(fig)


class TestStrategyPlotter:
    """Tests for StrategyPlotter class."""
    
    @pytest.mark.skipif(not HAS_MATPLOTLIB, reason="Matplotlib not available")
    def test_comprehensive_analysis(self):
        """Should create comprehensive strategy analysis plot."""
        plotter = StrategyPlotter(use_plotly=False)
        condor = create_iron_condor(
            90, 95, 105, 110,
            0.50, 2.00, 2.00, 0.50
        )
        
        fig = plotter.plot_strategy_analysis(
            strategy=condor,
            spot=100,
            min_price=80, max_price=120,
            time_to_expiry=0.25,
            volatility=0.20,
            risk_free_rate=0.05,
            show=False
        )
        
        assert fig is not None
        plt.close(fig)
    
    @pytest.mark.skipif(not HAS_MATPLOTLIB, reason="Matplotlib not available")
    def test_analysis_with_different_strategies(self):
        """Should work with various strategy types."""
        plotter = StrategyPlotter(use_plotly=False)
        
        strategies = [
            create_long_straddle(100, 3.00, 2.50),
            create_bull_call_spread(95, 105, 5.00, 2.00),
            create_iron_condor(90, 95, 105, 110, 0.50, 2.00, 2.00, 0.50)
        ]
        
        for strategy in strategies:
            fig = plotter.plot_strategy_analysis(
                strategy=strategy,
                spot=100,
                min_price=80, max_price=120,
                time_to_expiry=0.25,
                volatility=0.20,
                show=False
            )
            assert fig is not None
            plt.close(fig)


class TestPlotlyFigures:
    """Tests for plotly-specific figure features."""
    
    @pytest.mark.skipif(not HAS_PLOTLY, reason="Plotly not available")
    def test_plotly_interactive_features(self):
        """Plotly figure should have interactive features."""
        plotter = PayoffPlotter(use_plotly=True)
        straddle = create_long_straddle(100, 3.00, 2.50)
        
        fig = plotter.plot_payoff(
            strategy=straddle,
            min_price=80, max_price=120,
            show=False
        )
        
        # Check that figure has data traces
        assert len(fig.data) > 0
        
        # Check layout properties
        assert fig.layout.template is not None
    
    @pytest.mark.skipif(not HAS_PLOTLY, reason="Plotly not available")
    def test_plotly_html_export(self):
        """Should be able to export plotly figure to HTML."""
        plotter = PayoffPlotter(use_plotly=True)
        straddle = create_long_straddle(100, 3.00, 2.50)
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            temp_path = f.name
        
        try:
            fig = plotter.plot_payoff(
                strategy=straddle,
                min_price=80, max_price=120,
                show=False,
                save_path=temp_path
            )
            
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0
            
            # Check it's valid HTML
            with open(temp_path, 'r') as f:
                content = f.read()
                assert '<html' in content.lower() or 'plotly' in content.lower()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestVisualizationEdgeCases:
    """Tests for edge cases in visualization."""
    
    @pytest.mark.skipif(not HAS_MATPLOTLIB, reason="Matplotlib not available")
    def test_single_position_strategy(self):
        """Should handle single position strategy."""
        from src.options.payoff import Strategy
        
        strategy = Strategy("Single Call")
        strategy.add_position(create_long_call(100, 5.00))
        
        plotter = PayoffPlotter(use_plotly=False)
        fig = plotter.plot_payoff(
            strategy=strategy,
            min_price=80, max_price=120,
            show=False
        )
        
        assert fig is not None
        plt.close(fig)
    
    @pytest.mark.skipif(not HAS_MATPLOTLIB, reason="Matplotlib not available")
    def test_wide_price_range(self):
        """Should handle wide price ranges."""
        plotter = PayoffPlotter(use_plotly=False)
        straddle = create_long_straddle(100, 3.00, 2.50)
        
        fig = plotter.plot_payoff(
            strategy=straddle,
            min_price=50, max_price=150,
            num_points=200,
            show=False
        )
        
        assert fig is not None
        plt.close(fig)
    
    @pytest.mark.skipif(not HAS_MATPLOTLIB, reason="Matplotlib not available")
    def test_many_leg_strategy(self):
        """Should handle strategies with many legs."""
        from src.options.payoff import Strategy
        
        strategy = Strategy("Complex")
        for strike in [90, 95, 100, 105, 110]:
            strategy.add_position(create_long_call(strike, 2.00))
        
        plotter = PayoffPlotter(use_plotly=False)
        fig = plotter.plot_payoff(
            strategy=strategy,
            min_price=80, max_price=120,
            show=False
        )
        
        assert fig is not None
        plt.close(fig)
