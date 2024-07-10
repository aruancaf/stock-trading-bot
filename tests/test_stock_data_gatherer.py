import pytest
import stock_data_gatherer as sdg

def test_get_current_stock_data():
    """Test fetching current stock data"""
    stock_data = sdg.get_current_stock_data('AAPL')
    assert 'Close' in stock_data
    assert 'Open' in stock_data

def test_get_historical_data():
    """Test fetching historical stock data"""
    historical_data = sdg.get_historical_data('AAPL', '1mo', '1d')
    assert not historical_data.empty
    assert 'Close' in historical_data.columns
    assert 'Open' in historical_data.columns