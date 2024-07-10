import pytest
from runner import app  # Import the Flask app from runner.py

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_portfolio_endpoint(client):
    """Test the portfolio endpoint"""
    response = client.get('/portfolio')
    assert response.status_code == 200
    assert 'purchased' in response.get_json()
    assert 'sold' in response.get_json()

def test_portfolio_summary_endpoint(client):
    """Test the portfolio summary endpoint"""
    response = client.get('/portfolio/summary')
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'total_value' in json_data
    assert 'total_invested' in json_data
    assert 'current_balance' in json_data
    assert 'profit_loss' in json_data

def test_stock_details_endpoint(client):
    """Test the stock details endpoint"""
    response = client.get('/portfolio/details/AAPL')
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'Close' in json_data
    assert 'Open' in json_data