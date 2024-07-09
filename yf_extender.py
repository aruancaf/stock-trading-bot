import sys
from datetime import datetime

import yfinance as yf


def get_ticker_symbol(ticker: yf.Ticker) -> str:
    try:
        return ticker.get_info()['symbol']
    except ImportError:
        return ""


def get_stock_state(ticker: yf.Ticker) -> {}:
    stock_info = ticker.history("1d").iloc[0].to_dict()
    stock_info['Time'] = datetime.now().strftime("%H:%M:%S")
    del stock_info['Dividends']
    del stock_info['Stock Splits']
    return stock_info


# Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
def previous_high(ticker: yf.Ticker, time_period: str) -> float:
    high = 0
    stock_history = ticker.history(time_period)
    for i in range(0, len(stock_history) - 2):
        temp_high = stock_history.iloc[i].to_dict()['High']
        if temp_high > high:
            high = temp_high
    return high


# Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
def calculate_sma(ticker: yf.Ticker, time_period="1mo", interval="1d") -> float:
    stock_history = ticker.history(period=time_period, interval=interval)
    summation = 0
    time_period_days = 0
    for i in range(0, len(stock_history) - 1):
        summation += stock_history.iloc[i].to_dict()['Close']
        time_period_days += 1
    if time_period_days > 0:
        return summation / time_period_days
    return sys.maxsize


# Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
def calculate_ema(ticker: yf.Ticker, time_period="1mo") -> float:
    stock_history = ticker.history(period=time_period)
    return stock_history.iloc[len(stock_history) - 1].to_dict()['Close'] * (
                2.5 / (1 + len(stock_history))) + calculate_sma(ticker, time_period) * (
                   1 - (2.5 / (1 + len(stock_history))))


# Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
def calculate_previous_ema(ticker: yf.Ticker, time_period="1mo", days_previous=1) -> float:
    time_period_days = len(ticker.history(period=time_period))
    stock_history = ticker.history(period=time_period)
    return stock_history.iloc[time_period_days - days_previous - 1].to_dict()['Close'] * (
            2.5 / (1 + time_period_days)) + calculate_sma(ticker, time_period) * (
                   1 - (2.5 / (1 + time_period_days)))


def get_high2current_price_change_percent(ticker: yf.Ticker) -> float:
    stock_info = ticker.history("1d").iloc[0].to_dict()
    return (stock_info['Close'] - stock_info['High']) / stock_info['High']


def get_direction(ticker: yf.Ticker) -> float:
    stock_history = ticker.history(period="1d", interval="1m")
    return (stock_history.iloc[len(stock_history) - 1].to_dict()['Close'] - stock_history.iloc[len(stock_history) - 2].to_dict()['Close'])/stock_history.iloc[len(stock_history) - 2].to_dict()['Close']
