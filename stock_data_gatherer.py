import pandas as pd
import finnhub
from typing import Dict, Any
import psycopg2
from psycopg2.extras import Json
from diskcache import Cache
import os
import constants
from dotenv import load_dotenv
import util
import yfinance as yf
import requests

# Load environment variables
load_dotenv()

# Initialize cache
cache = Cache('./stock_data_cache')
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
MORNINGSTAR_API_KEY = os.getenv("MORNINGSTAR_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# Initialize Finnhub client
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
print(f"Finnhub API Key: {FINNHUB_API_KEY}")

# Check if the API key is None or empty
if not FINNHUB_API_KEY:
    raise ValueError("Finnhub API Key is not set. Please check your .env file.")

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
# Initialize the error log
error_log = []

# Function to get historical data
def get_historical_data(ticker_symbol: str, time_period: str, time_interval: str) -> pd.DataFrame:
    symbol_time_periods = {
        "PLA": "1mo",
        "IOO": "1mo",
    }

    if ticker_symbol in symbol_time_periods:
        time_period = symbol_time_periods[ticker_symbol]

    valid_periods = ['1mo', '3mo', '6mo', 'ytd', '1y', '2y', '5y', '10y', 'max']
    if time_period not in valid_periods:
        time_period = '5d'

    data = yf.Ticker(ticker_symbol).history(period=time_period, interval=time_interval)
    if 'Close' in data.columns:
        data.rename(columns={'Close': 'price'}, inplace=True)
    else:
        raise KeyError(f"The 'Close' column is missing in the data for {ticker_symbol}")

    data['date'] = data.index
    data.reset_index(drop=True, inplace=True)
    return data

# Function to get current stock data
def get_current_stock_data(ticker_symbol: str) -> Dict[str, Any]:
    cache_key = f"{ticker_symbol}_current_stock_data"
    if cache_key in cache:
        return cache[cache_key]

    stock_data = {}
    
    try:
        finnhub_data = finnhub_client.quote(ticker_symbol)
        stock_data = {
            'date': pd.Timestamp.now().isoformat(),
            'price': finnhub_data['c'],
            'Finnhub_Open': finnhub_data['o'],
            'Finnhub_High': finnhub_data['h'],
            'Finnhub_Low': finnhub_data['l'],
            'Finnhub_Prev_Close': finnhub_data['pc'],
            'Finnhub_Volume': finnhub_data['v']
        }
    except finnhub.exceptions.FinnhubAPIException as e:
        print(f"No data found for ticker symbol {ticker_symbol}: {e}")
        stock_data = get_morningstar_data(ticker_symbol)

    try:
        historical_stock_data = finnhub_client.stock_candles(ticker_symbol, 'D', int(pd.Timestamp('2018-01-01').timestamp()), int(pd.Timestamp('2023-01-01').timestamp()))
        
        if not historical_stock_data or 'c' not in historical_stock_data:
            raise ValueError(f"No historical data found for ticker symbol {ticker_symbol}")

        close_prices = pd.Series(historical_stock_data['c'])
        stock_data.update({
            'SMA': util.calculate_sma(close_prices)[0],
            'PREVSMA': util.calculate_sma(close_prices)[1],
            'EMA': util.calculate_ema(close_prices),
            'PREVPRICE': close_prices.iloc[-2] if len(close_prices) > 1 else None,
            'TRIX': util.calculate_trix(close_prices)[0],
            'PREVTRIX': util.calculate_trix(close_prices)[1],
            'AROON_UP': util.calculate_aroon(close_prices)[0],
            'AROON_DOWN': util.calculate_aroon(close_prices)[1],
            'BULL_POWER': util.calculate_elder_ray(close_prices)[0],
            'BEAR_POWER': util.calculate_elder_ray(close_prices)[1],
            'HEIKIN_ASHI_CLOSE': util.calculate_heikin_ashi(close_prices),
            'PSAR': util.calculate_parabolic_sar(close_prices),
            'RSI': util.calculate_rsi(close_prices)
        })
    except Exception as e:
        print(f"Error calculating indicators for {ticker_symbol}: {e}")

    if not stock_data:
        try:
            stock_data = get_yahoo_finance_data(ticker_symbol)
        except Exception as e:
            print(f"Error fetching data from Yahoo Finance for {ticker_symbol}: {e}")
    
    if not stock_data:
        try:
            stock_data = get_morningstar_data(ticker_symbol)
        except Exception as e:
            print(f"Error fetching data from Morningstar for {ticker_symbol}: {e}")

    cache[cache_key] = stock_data
    return stock_data

def get_yahoo_finance_data(ticker_symbol: str) -> Dict[str, Any]:
    try:
        historical_stock_data = get_historical_data(ticker_symbol, '5d', '2m')
        stock_data = historical_stock_data.iloc[-1].to_dict()
        del stock_data['Dividends']
        del stock_data['Stock Splits']
        
        stock_data.update({
            'SMA': util.calculate_sma(historical_stock_data)[0],
            'PREVSMA': util.calculate_sma(historical_stock_data)[1],
            'EMA': util.calculate_ema(historical_stock_data),
            'PREVPRICE': historical_stock_data.iloc[-2].to_dict()['price'] if len(historical_stock_data) > 1 else None,
            'date': historical_stock_data['date'].iloc[-1],
            'price': historical_stock_data['price'].iloc[-1]
        })

        return stock_data
    except Exception as e:
        print(f"Error fetching data from Yahoo Finance for {ticker_symbol}: {e}")
        return {}

def get_morningstar_data(ticker_symbol: str) -> Dict[str, Any]:
    url = "https://morning-star.p.rapidapi.com/stock/v2/get-realtime-data"
    querystring = {"performanceId": ticker_symbol}
    headers = {
        "x-rapidapi-host": "morning-star.p.rapidapi.com",
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY")
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        return {
            'date': pd.Timestamp.now().isoformat(),
            'price': data['price'],
            'Morningstar_Open': data['open'],
            'Morningstar_High': data['high'],
            'Morningstar_Low': data['low'],
            'Morningstar_Price': data['price'],
            'Morningstar_Prev_Close': data['prev_close'],
            'Morningstar_Volume': data['volume']
        }
    else:
        print(f"Error fetching data from Morningstar for {ticker_symbol}: {response.status_code}")
        return {}

def get_price_slope(ticker_symbol: str):
    n = 5
    historical_stock_data = get_historical_data(ticker_symbol, '5d', '1m')
    close_prices = historical_stock_data['price'][-n:]
    return util.linear_regress_slope(1, close_prices)

def get_volume_slope(ticker_symbol: str):
    n = 5
    historical_stock_data = get_historical_data(ticker_symbol, '5d', '1m')
    volume_by_time = historical_stock_data['Volume'][-n:]
    return util.linear_regress_slope(1, volume_by_time)

def get_stock_company_name(ticker_symbol: str):
    try:
        company_info = finnhub_client.company_profile2(symbol=ticker_symbol)
        return company_info['name']
    except Exception as e:
        return "Unknown"

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
    try:
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
    except Exception as e:
        print(f"Error storing data for {ticker_symbol}: {e}")
        conn.rollback()

if __name__ == "__main__":
    error_log = []
    for ticker in constants.STOCKS_TO_CHECK:
        try:
            stock_data = get_current_stock_data(ticker)
            stock_data['price_slope'] = get_price_slope(ticker)
            stock_data['volume_slope'] = get_volume_slope(ticker)
            stock_data['company_name'] = get_stock_company_name(ticker)
            stock_data['date'] = pd.Timestamp.now().isoformat()
            stock_data['price'] = stock_data.get('price')
            store_stock_data_in_db(ticker, stock_data)
            print(f"Stored data for {ticker}")
        except ValueError as e:
            print(e)
            error_log.append((ticker, str(e)))
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            error_log.append((ticker, str(e)))
    
    # Write errors to a log file
    with open('error_log.txt', 'w') as f:
        for error in error_log:
            f.write(f"{error[0]}: {error[1]}\n")

    # Close the database connection and cache
    cache.close()
    cursor.close()
    conn.close()