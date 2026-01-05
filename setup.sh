#!/bin/bash

echo "=========================================="
echo "Algorithmic Trading System Setup"
echo "=========================================="
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "Creating data and logs directories..."
mkdir -p data logs

# Copy environment example
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file with your API keys if needed"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run a simple backtest example:"
echo "  python example_backtest.py"
echo ""
echo "To run a full backtest:"
echo "  python main.py --mode backtest --symbols SPY --strategy sma"
echo ""
echo "To see all options:"
echo "  python main.py --help"
echo ""
echo "To run tests:"
echo "  pytest tests/ -v"
echo ""
