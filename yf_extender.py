import sys
from datetime import datetime
import yfinance as yf
import util
import logging

def get_ticker_symbol(ticker: yf.Ticker) -> str:
    try:
        return ticker.info['symbol']
    except ImportError:
        return ""

def previous_high(ticker_symbol: str, time_period: str) -> float:
    ticker = yf.Ticker(ticker_symbol)
    stock_history = ticker.history(period=time_period)
    
    if stock_history.empty:
        logging.warning(f"No data available for ticker {ticker_symbol}")
        return None
    
    return stock_history['High'].max()

def get_stock_state(ticker_symbol: str) -> dict:
    ticker = yf.Ticker(ticker_symbol)
    history = ticker.history(period="1d")
    
    if history.empty:
        logging.warning(f"No data available for ticker {ticker_symbol}")
        return None

    stock_info = history.iloc[0].to_dict()
    stock_info['Time'] = datetime.now().strftime("%H:%M:%S")
    del stock_info['Dividends']
    del stock_info['Stock Splits']
    
    return stock_info

# Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
def calculate_sma(ticker: yf.Ticker, time_period="1mo", interval="1d") -> float:
    stock_history = ticker.history(period=time_period, interval=interval)
    summation = sum(stock_history['Close'])
    time_period_days = len(stock_history)
    return summation / time_period_days if time_period_days > 0 else sys.maxsize

# Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
def calculate_ema(ticker: yf.Ticker, time_period="1mo") -> float:
    stock_history = ticker.history(period=time_period)
    return (
        stock_history['Close']
        .ewm(span=len(stock_history), adjust=False)
        .mean()
        .iloc[-1]
    )

# Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
def calculate_previous_ema(ticker: yf.Ticker, time_period="1mo", days_previous=1) -> float:
    stock_history = ticker.history(period=time_period)
    return (
        stock_history['Close']
        .ewm(span=len(stock_history), adjust=False)
        .mean()
        .iloc[-days_previous - 1]
    )

def get_high2current_price_change_percent(ticker: yf.Ticker) -> float:
    stock_info = ticker.history(period="1d").iloc[0].to_dict()
    return (stock_info['Close'] - stock_info['High']) / stock_info['High']

def get_direction(ticker: yf.Ticker) -> float:
    stock_history = ticker.history(period="1d", interval="1m")
    return (stock_history.iloc[-1]['Close'] - stock_history.iloc[-2]['Close']) / stock_history.iloc[-2]['Close']

def get_historical_data(ticker_symbol: str, time_period: str, time_interval: str) -> yf.Ticker:
    return yf.Ticker(ticker_symbol).history(period=time_period, interval=time_interval)

def get_current_stock_data(ticker_symbol: str) -> dict:
    historical_stock_data = get_historical_data(ticker_symbol, '1d', '3m')
    stock_data = historical_stock_data.iloc[0].to_dict()
    
    stock_data['SMA'] = calculate_sma(yf.Ticker(ticker_symbol))
    stock_data['PREVSMA'] = calculate_sma(yf.Ticker(ticker_symbol), time_period="1mo", interval="1d")
    stock_data['EMA'] = calculate_ema(yf.Ticker(ticker_symbol))
    stock_data['PREVPRICE'] = historical_stock_data.iloc[-2]['Close']

    # Calculate TRIX
    stock_data['TRIX'], stock_data['PREVTRIX'] = util.calculate_trix(historical_stock_data)

    # Calculate Aroon
    stock_data['AROON_UP'], stock_data['AROON_DOWN'] = util.calculate_aroon(historical_stock_data)

    # Calculate Elder Ray
    stock_data['BULL_POWER'], stock_data['BEAR_POWER'] = util.calculate_elder_ray(historical_stock_data)

    return stock_data

def get_price_slope(ticker_symbol: str):
    n = 5
    historical_stock_data = get_historical_data(ticker_symbol, '1d', '1m')
    stock_price_by_time = [historical_stock_data.iloc[i]['Close'] for i in range(-n, 0)]
    return util.linear_regress_slope(range(n), stock_price_by_time)

def get_volume_slope(ticker_symbol: str):
    n = 5
    historical_stock_data = get_historical_data(ticker_symbol, '1d', '1m')
    stock_volume_by_time = [historical_stock_data.iloc[i]['Volume'] for i in range(-n, 0)]
    return util.linear_regress_slope(range(n), stock_volume_by_time)

def get_stock_company_name(ticker_symbol: str):
    return yf.Ticker(ticker_symbol).info['longName']