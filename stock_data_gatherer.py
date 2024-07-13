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
    ticker TEXT UNIQUE NOT NULL
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
        else:
            print(f"No data found for {ticker}")
    
    conn.close()
    print("Completed the stock data gathering process.")