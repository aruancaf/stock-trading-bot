import pandas as pd
import requests
from typing import List, Dict, Any
from diskcache import Cache
import os
from dotenv import load_dotenv
import util
import time
import scraper  # Import the scraper module

# Load environment variables
load_dotenv()

# Fetch API key from environment variables
QUANDL_API_KEY = os.getenv('QUANDL_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# Define the API key directly for testing if it is not loaded from the environment
if not QUANDL_API_KEY:
    QUANDL_API_KEY = 'your_quandl_api_key_here'
if not ALPHA_VANTAGE_API_KEY:
    ALPHA_VANTAGE_API_KEY = 'your_alpha_vantage_api_key_here'

# Initialize cache
cache = Cache('./stock_data_cache')

# Initialize the error log
error_log = []

# Lists to store stocks with available data
stocks_with_current_data = []
stocks_with_historical_data = []

# Function to fetch historical data from Nasdaq
def get_historical_data(symbol: str, time_period: str = '1yr', time_interval: str = '5m') -> pd.DataFrame:
    url = f"https://data.nasdaq.com/api/v3/datasets/WIKI/{symbol}/data.json"
    params = {"api_key": QUANDL_API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        dataset_data = data.get("dataset_data", {})
        historical_data = dataset_data.get("data", [])
        columns = dataset_data.get("column_names", [])

        if not historical_data:
            print(f"No historical data found for {symbol}")
            return None
        df = pd.DataFrame(historical_data, columns=columns)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        print(f"Historical data available for {symbol}")
        return df
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            print(f"404 Error: No historical data found for {symbol}")
            return None
        else:
            print(f"HTTP error occurred for {symbol}: {http_err}")
            return None
    except Exception as e:
        print(f"Error fetching historical data for {symbol}: {e}")
        return None

# Function to get current stock data from Alpha Vantage
def get_current_stock_data_alpha_vantage(ticker_symbol: str) -> Dict[str, Any]:
    cache_key = f"{ticker_symbol}_current_stock_data"
    if cache_key in cache:
        return cache[cache_key]

    url = f"https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker_symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json().get('Global Quote', {})
        if not data:
            print(f"No current data found for {ticker_symbol}")
            return {}

        current_stock_data = {
            'date': pd.Timestamp.now().isoformat(),
            'price': data.get('05. price', None),
            'Alpha_Open': data.get('02. open', None),
            'Alpha_High': data.get('03. high', None),
            'Alpha_Low': data.get('04. low', None),
            'Alpha_Prev_Close': data.get('08. previous close', None),
            'Alpha_Volume': data.get('06. volume', None)
        }

        print(f"Current data available for {ticker_symbol}")
        return current_stock_data
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 429:
            print(f"Rate limit exceeded for {ticker_symbol}. Retrying...")
            time.sleep(2)  # Wait for 2 seconds before retrying
            return get_current_stock_data_alpha_vantage(ticker_symbol)
        else:
            print(f"HTTP error occurred for {ticker_symbol}: {http_err}")
    except Exception as e:
        print(f"Error fetching current data for {ticker_symbol}: {e}")
        return {}

# Function to process stock data
def process_stock_data(ticker: str) -> Dict[str, Any]:
    stock_data = get_current_stock_data_alpha_vantage(ticker)
    if not stock_data:
        print(f"No data found for {ticker}")
        return None

    # Process stock data
    stock_data['price_slope'] = get_price_slope(ticker)
    stock_data['volume_slope'] = get_volume_slope(ticker)
    stock_data['company_name'] = get_stock_company_name(ticker)
    stock_data['date'] = pd.Timestamp.now().isoformat()
    stock_data['price'] = stock_data.get('price')
    print(f"Processed data for {ticker}: {stock_data}")

    return stock_data

# Function to get price slope
def get_price_slope(ticker_symbol: str):
    n = 5
    historical_stock_data = get_historical_data(ticker_symbol)
    if historical_stock_data is None:
        return None
    close_prices = historical_stock_data['Adj. Close'][-n:]
    return util.linear_regress_slope(1, close_prices)

# Function to get volume slope
def get_volume_slope(ticker_symbol: str):
    n = 5
    historical_stock_data = get_historical_data(ticker_symbol)
    if historical_stock_data is None:
        return None
    volume_by_time = historical_stock_data['Adj. Volume'][-n:]
    return util.linear_regress_slope(1, volume_by_time)

# Function to get stock company name
def get_stock_company_name(ticker_symbol: str):
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": ticker_symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('Name', 'Unknown')
    except Exception as e:
        print(f"Error fetching company name for {ticker_symbol}: {e}")
    return "Unknown"

def get_valid_tickers(tickers: List[str]) -> List[str]:
    valid_tickers = []
    for ticker in tickers:
        try:
            if data := get_current_stock_data_alpha_vantage(ticker):
                valid_tickers.append(ticker)
        except Exception as e:
            print(f"{ticker}: possibly delisted; {e}")
    return valid_tickers

def get_stocks_with_current_data() -> List[str]:
    return stocks_with_current_data

def get_stocks_with_historical_data() -> List[str]:
    return stocks_with_historical_data

if __name__ == "__main__":
    # Load tickers from TICKERS.csv using the correct path
    tickers_df = pd.read_csv('/Users/chefsbae/stock-trading-bot/TICKERS.csv')
    print("TICKERS.csv columns:", tickers_df.columns)
    tickers_from_tickers_csv = tickers_df['TICKERS'].tolist()  # Adjusted to match your CSV column name

    # Use scraper module to get tickers from All_Scraped_Tickers.csv
    all_scraped_tickers = scraper.scrape_all_urls()
    tickers_from_all_scraped_csv = [ticker['Ticker'] for ticker in all_scraped_tickers]  # Adjusted to match your scraped data format

    # Combine tickers from both files
    combined_tickers = list(set(tickers_from_tickers_csv + tickers_from_all_scraped_csv))

    error_log = []

    for ticker in combined_tickers:
        try:
            stock_data = process_stock_data(ticker)
            if not stock_data:
                continue

            # Categorize stocks
            if 'price' in stock_data and stock_data['price'] is not None:
                stocks_with_current_data.append(ticker)
            if stock_data.get('historical_data_available', False):
                stocks_with_historical_data.append(ticker)

            # Wait before the next request to avoid rate limiting
            time.sleep(2)  # Adjust the sleep time as needed

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

    # Close the cache
    cache.close()

    # Print summary of stocks with data
    print("\nStocks with current data available:")
    for stock in stocks_with_current_data:
        print(stock)

    print("\nStocks with historical data available:")
    for stock in stocks_with_historical_data:
        print(stock)