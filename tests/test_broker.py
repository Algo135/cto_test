import pytest
from src.paper_trading.virtual_broker import VirtualBroker
from src.execution.order import Order, OrderType, OrderSide, OrderStatus


@pytest.fixture
def broker():
    return VirtualBroker(initial_capital=100000)


def test_virtual_broker_initialization(broker):
    assert broker.initial_capital == 100000
    assert broker.portfolio.cash == 100000


def test_submit_buy_order(broker):
    broker.update_prices({'TEST': 50.0})
    
    order = Order(
        symbol='TEST',
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        quantity=100
    )
    
    order_id = broker.submit_order(order)
    
    assert order_id is not None
    assert order.status == OrderStatus.FILLED
    assert order.filled_quantity == 100


def test_submit_sell_order(broker):
    broker.update_prices({'TEST': 50.0})
    
    broker.portfolio.update_position('TEST', 100, 50.0, 'BUY')
    
    order = Order(
        symbol='TEST',
        order_type=OrderType.MARKET,
        side=OrderSide.SELL,
        quantity=100
    )
    
    order_id = broker.submit_order(order)
    
    assert order_id is not None
    assert order.status == OrderStatus.FILLED


def test_get_account_info(broker):
    account_info = broker.get_account_info()
    
    assert 'cash' in account_info
    assert 'portfolio_value' in account_info
    assert account_info['cash'] == 100000


def test_get_positions_empty(broker):
    positions = broker.get_positions()
    
    assert len(positions) == 0


def test_get_positions_with_position(broker):
    broker.update_prices({'TEST': 50.0})
    broker.portfolio.update_position('TEST', 100, 50.0, 'BUY')
    
    positions = broker.get_positions()
    
    assert len(positions) == 1
    assert positions[0]['symbol'] == 'TEST'
    assert positions[0]['quantity'] == 100


def test_cancel_order(broker):
    order = Order(
        symbol='TEST',
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        quantity=100
    )
    
    order.order_id = 'test_order_123'
    order.status = OrderStatus.PENDING
    broker.orders[order.order_id] = order
    
    result = broker.cancel_order('test_order_123')
    
    assert result is True
    assert order.status == OrderStatus.CANCELLED
