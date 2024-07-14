import os
import pandas as pd
from dotenv import load_dotenv
import yfinance as yf
import sqlite3
import logging
import scraper  # Import the scraper module

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(filename='stock_data_gatherer.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection
db_path = os.getenv("DB_PATH", "stocks.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT UNIQUE NOT NULL,
    company_name TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS historical_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER,
    date DATE,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT,
    FOREIGN KEY(stock_id) REFERENCES stocks(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS current_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER,
    date DATE,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT,
    FOREIGN KEY(stock_id) REFERENCES stocks(id)
)
''')

conn.commit()

def get_data_yfinance(ticker: str, period: str = '5y', interval: str = '1d'):
    try:
        data = yf.Ticker(ticker).history(period=period, interval=interval)
        data.reset_index(inplace=True)
        data.columns = data.columns.str.lower()
        logging.info(f"Fetched data for {ticker} from Yahoo Finance")
        return data
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

def get_current_stock_data(ticker: str):
    try:
        # Ensure ticker is a string and not a dictionary
        if isinstance(ticker, dict):
            ticker = ticker.get('Ticker', '')

        if not isinstance(ticker, str) or not ticker:
            raise ValueError(f"Invalid ticker value: {ticker}")

        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        data.reset_index(inplace=True)
        data.columns = data.columns.str.lower()
        logging.info(f"Fetched current data for {ticker} from Yahoo Finance")
        return data
    except Exception as e:
        logging.error(f"Error fetching current data for {ticker}: {e}")
        return pd.DataFrame()

def get_stock_company_name(ticker: str):
    try:
        # Ensure ticker is a string and not a dictionary
        if isinstance(ticker, dict):
            ticker = ticker.get('Ticker', '')

        if not isinstance(ticker, str) or not ticker:
            raise ValueError(f"Invalid ticker value: {ticker}")

        company_info = yf.Ticker(ticker).info
        company_name = company_info.get('longName', 'Unknown')
        logging.info(f"Fetched company name for {ticker}: {company_name}")
        return company_name
    except Exception as e:
        logging.error(f"Error fetching company name for {ticker}: {e}")
        return "Unknown"

def get_price_slope(ticker: str, period: str = '1y', interval: str = '1d'):
    data = get_data_yfinance(ticker, period, interval)
    data['slope'] = data['close'].diff().rolling(window=5).mean()
    return None if data.empty else data['slope'].iloc[-1]

def get_volume_slope(ticker: str, period: str = '1y', interval: str = '1d'):
    data = get_data_yfinance(ticker, period, interval)
    data['volume_slope'] = data['volume'].diff().rolling(window=5).mean()
    return None if data.empty else data['volume_slope'].iloc[-1]

def store_historical_data(ticker: str, data: pd.DataFrame):
    try:
        cursor.execute("INSERT OR IGNORE INTO stocks (ticker) VALUES (?)", (ticker,))
        cursor.execute("SELECT id FROM stocks WHERE ticker = ?", (ticker,))
        stock_id = cursor.fetchone()[0]

        for _, row in data.iterrows():
            cursor.execute('''
            INSERT INTO historical_data (stock_id, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (stock_id, row['date'].strftime('%Y-%m-%d'), row['open'], row['high'], row['low'], row['close'], row['volume']))

        conn.commit()
        logging.info(f"Stored historical data for {ticker}")
        print(f"Stored historical data for {ticker}")
    except Exception as e:
        logging.error(f"Error storing data for {ticker}: {e}")
        print(f"Error storing data for {ticker}: {e}")

def store_current_data(ticker: str, data: pd.DataFrame):
    try:
        cursor.execute("INSERT OR IGNORE INTO stocks (ticker) VALUES (?)", (ticker,))
        cursor.execute("SELECT id FROM stocks WHERE ticker = ?", (ticker,))
        stock_id = cursor.fetchone()[0]

        for _, row in data.iterrows():
            cursor.execute('''
            INSERT INTO current_data (stock_id, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (stock_id, row['date'].strftime('%Y-%m-%d %H:%M:%S'), row['open'], row['high'], row['low'], row['close'], row['volume']))

        conn.commit()
        logging.info(f"Stored current data for {ticker}")
        print(f"Stored current data for {ticker}")
    except Exception as e:
        logging.error(f"Error storing current data for {ticker}: {e}")
        print(f"Error storing current data for {ticker}: {e}")

def store_stock_data_in_db(ticker: str, stock_data: dict):
    try:
        company_name = get_stock_company_name(ticker)
        cursor.execute("INSERT OR IGNORE INTO stocks (ticker, company_name) VALUES (?, ?)", (ticker, company_name))

        cursor.execute("SELECT id FROM stocks WHERE ticker = ?", (ticker,))
        stock_id = cursor.fetchone()[0]

        if 'historical_data' in stock_data:
            for _, row in stock_data['historical_data'].iterrows():
                cursor.execute('''
                INSERT INTO historical_data (stock_id, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (stock_id, row['date'].strftime('%Y-%m-%d'), row['open'], row['high'], row['low'], row['close'], row['volume']))

        if 'current_data' in stock_data:
            for _, row in stock_data['current_data'].iterrows():
                cursor.execute('''
                INSERT INTO current_data (stock_id, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (stock_id, row['date'].strftime('%Y-%m-%d %H:%M:%S'), row['open'], row['high'], row['low'], row['close'], row['volume']))

        conn.commit()
        logging.info(f"Stored stock data for {ticker} in the database")
        print(f"Stored stock data for {ticker} in the database")
    except Exception as e:
        logging.error(f"Error storing stock data for {ticker}: {e}")
        print(f"Error storing stock data for {ticker}: {e}")

def scrape_all_tickers():
    all_scraped_tickers = scraper.scrape_all_urls()
    return [ticker['Ticker'] for ticker in all_scraped_tickers]

def get_all_tickers(conn):
    """Fetch all tickers from the database."""
    query = "SELECT ticker FROM stocks"
    tickers = pd.read_sql(query, conn)
    return tickers['ticker'].tolist()

if __name__ == "__main__":
    print("Starting the stock data gathering process...")
    tickers = scrape_all_tickers()
    total_tickers = len(tickers)
    print(f"Total tickers to process: {total_tickers}")

    for index, ticker in enumerate(tickers, start=1):
        print(f"Processing {ticker} ({index}/{total_tickers})")
        data = get_data_yfinance(ticker)
        if not data.empty:
            store_historical_data(ticker, data)
            store_current_data(ticker, data)
        else:
            print(f"No data found for {ticker}")

    conn.close()
    print("Completed the stock data gathering process.")