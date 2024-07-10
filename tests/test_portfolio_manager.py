import pytest
import portfolio_manager

def test_buy_stock():
    """Test buying a stock"""
    portfolio_manager.buy_stock('AAPL', 10)
    assert 'AAPL' in portfolio_manager.purchased
    assert portfolio_manager.purchased['AAPL']['Quantity'] == 10

def test_sell_stock():
    """Test selling a stock"""
    portfolio_manager.buy_stock('AAPL', 10)
    portfolio_manager.sell_stock('AAPL')
    assert 'AAPL' not in portfolio_manager.purchased

def test_get_transaction_history():
    """Test getting transaction history"""
    history = portfolio_manager.get_transaction_history()
    assert isinstance(history, list)