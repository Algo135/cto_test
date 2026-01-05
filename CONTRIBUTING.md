# Contributing to Algorithmic Trading System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/algo-trading-system.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest tests/ -v`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Run tests
pytest tests/ -v
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for classes and public methods
- Keep functions focused and small
- Use meaningful variable names

### Formatting

We use `black` for code formatting:

```bash
black src/ tests/
```

### Linting

Run `flake8` before submitting:

```bash
flake8 src/ tests/ --max-line-length=100
```

## Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Aim for high code coverage (>80%)

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Adding New Strategies

To add a new trading strategy:

1. Create a new class in `src/strategy/example_strategies.py` or a new file
2. Inherit from `BaseStrategy`
3. Implement required methods:
   - `generate_signals()`: For backtesting
   - `on_bar()`: For real-time trading
4. Add tests in `tests/test_strategy.py`
5. Document the strategy in README.md

Example:

```python
class MyStrategy(BaseStrategy):
    def __init__(self, param1, param2):
        super().__init__(name="MyStrategy")
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> List[Signal]:
        # Your logic here
        pass
    
    def on_bar(self, bar_event) -> Optional[Signal]:
        # Your logic here
        pass
```

## Adding New Brokers

To add a new broker:

1. Create a new file in `src/execution/`
2. Inherit from `Broker` abstract class
3. Implement all required methods
4. Add tests in `tests/test_broker.py`

## Pull Request Guidelines

- Write clear, descriptive commit messages
- Reference related issues in PR description
- Include tests for new features
- Update documentation as needed
- Ensure CI/CD checks pass

## Reporting Bugs

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/stack traces
- Relevant code snippets

## Feature Requests

For feature requests:

- Explain the use case
- Describe the proposed solution
- Consider alternatives
- Be open to discussion

## Code Review Process

1. Maintainers will review your PR
2. Address any feedback
3. Once approved, PR will be merged
4. Your contribution will be credited

## Community Guidelines

- Be respectful and constructive
- Welcome newcomers
- Focus on the code, not the person
- Give credit where due

## Areas for Contribution

- New trading strategies
- Additional brokers/exchanges
- Performance optimizations
- Documentation improvements
- Bug fixes
- Test coverage
- Example notebooks
- Visualization enhancements

## Questions?

Feel free to open an issue for questions or discussion.

Thank you for contributing! 🎉
