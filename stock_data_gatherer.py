import pandas as pd
import yfinance as yf
import util
from typing import Dict, Any
import psycopg2
from psycopg2.extras import Json
from diskcache import Cache
import os
import constants
# Initialize cache
cache = Cache('./stock_data_cache')

# Database credentials
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Connect to the database
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()
# @param ticker_symbol - str
# @param time_period - Valid Periods: 1d, 5d, 1mo,3mo,6mo,1y,2y,5y,10y,ytd,maxi
# @param time_interval - Valid Periods:`1m , 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
def get_historical_data(ticker_symbol: str, time_period: str, time_interval: str):
    if isinstance(ticker_symbol, dict):
        ticker_symbol = ticker_symbol.get('symbol', '')
    return yf.Ticker(ticker_symbol).history(period=time_period, interval=time_interval)

def get_current_stock_data(ticker_symbol: str) -> Dict[str, Any]:
    cache_key = f"{ticker_symbol}_current_stock_data"
    if cache_key in cache:
        return cache[cache_key]

    historical_stock_data = get_historical_data(ticker_symbol, '3mo', '5m')
    stock_data = historical_stock_data.iloc[-1].to_dict()
  
    del stock_data['Dividends']
    del stock_data['Stock Splits']

    stock_data['SMA'] = util.calculate_sma(historical_stock_data)[0]
    stock_data['PREVSMA'] = util.calculate_sma(historical_stock_data)[1]
    stock_data['EMA'] = util.calculate_ema(historical_stock_data)
    stock_data['PREVPRICE'] = historical_stock_data.iloc[-2]['Close']

    trix_current, trix_previous = util.calculate_trix(historical_stock_data)
    stock_data['TRIX'] = trix_current
    stock_data['PREVTRIX'] = trix_previous

    aroon_up, aroon_down = util.calculate_aroon(historical_stock_data)
    stock_data['AROON_UP'] = aroon_up
    stock_data['AROON_DOWN'] = aroon_down

    bull_power, bear_power = util.calculate_elder_ray(historical_stock_data)
    stock_data['BULL_POWER'] = bull_power
    stock_data['BEAR_POWER'] = bear_power

    stock_data['HEIKIN_ASHI_CLOSE'] = util.calculate_heikin_ashi(historical_stock_data)
    stock_data['PSAR'] = util.calculate_parabolic_sar(historical_stock_data)
    stock_data['RSI'] = util.calculate_rsi(historical_stock_data)

    cache[cache_key] = stock_data  # Cache the stock data

    return stock_data

def get_price_slope(ticker_symbol: str):
    n = 5
    historical_stock_data = get_historical_data(ticker_symbol, '1d', '1m')
    stock_price_by_time = [historical_stock_data.iloc[i].to_dict()['Close'] for i in range(-n, 0)]
    return util.linear_regress_slope(1, stock_price_by_time)

def get_volume_slope(ticker_symbol: str):
    n = 5
    historical_stock_data = get_historical_data(ticker_symbol, '1d', '1m')
    stock_volume_by_time = [historical_stock_data.iloc[i].to_dict()['Volume'] for i in range(-n, 0)]
    return util.linear_regress_slope(1, stock_volume_by_time)

def get_stock_company_name(ticker_symbol: str):
    return yf.Ticker(ticker_symbol).info['longName']

def get_valid_tickers(tickers):
    valid_tickers = []
    for ticker in tickers:
        try:
            if data := get_current_stock_data(ticker):
                valid_tickers.append(ticker)
        except Exception as e:
            print(f"${ticker}: possibly delisted; {e}")
    return valid_tickers

def store_stock_data_in_db(ticker_symbol: str, stock_data: Dict[str, Any]):
    cursor.execute(
        """
        INSERT INTO stock_data (ticker_symbol, data, fetched_at)
        VALUES (%s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (ticker_symbol) DO UPDATE
        SET data = EXCLUDED.data, fetched_at = EXCLUDED.fetched_at;
        """,
        (ticker_symbol, Json(stock_data))
    )
    conn.commit()


if __name__ == "__main__":
    for ticker in constants.STOCKS_TO_CHECK:
        stock_data = get_current_stock_data(ticker)
        stock_data['price_slope'] = get_price_slope(ticker)
        stock_data['volume_slope'] = get_volume_slope(ticker)
        stock_data['company_name'] = get_stock_company_name(ticker)
        store_stock_data_in_db(ticker, stock_data)
        print(f"Stored data for {ticker}")

    # Close the database connection and cache
    cache.close()
    cursor.close()
    conn.close()