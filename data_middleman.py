import sqlite3
import pandas as pd

def connect_to_db(db_path="stocks.db"):
    """Connect to the SQLite database."""
    return sqlite3.connect(db_path)

def get_historical_data(conn, ticker):
    """Fetch historical data for a given ticker from the database."""
    query = """
    SELECT date, open, high, low, close, volume
    FROM historical_data
    JOIN stocks ON historical_data.stock_id = stocks.id
    WHERE stocks.ticker = ?
    """
    try:
        return pd.read_sql(query, conn, params=(ticker,))
    except Exception as e:
        print(f"Error fetching historical data for {ticker}: {e}")
        return pd.DataFrame()

def get_current_data(conn, ticker):
    """Fetch current data for a given ticker from the database."""
    query = """
    SELECT date, open, high, low, close, volume
    FROM current_data
    JOIN stocks ON current_data.stock_id = stocks.id
    WHERE stocks.ticker = ?
    """
    try:
        return pd.read_sql(query, conn, params=(ticker,))
    except Exception as e:
        print(f"Error fetching current data for {ticker}: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    db_path = "stocks.db"
    conn = connect_to_db(db_path)

    ticker = "AAPL"  # Example ticker
    print(f"Fetching historical data for {ticker}...")
    historical_data = get_historical_data(conn, ticker)
    if not historical_data.empty:
        print(f"Historical data for {ticker}:")
        print(historical_data.head())
    else:
        print(f"No historical data found for {ticker}")

    print(f"Fetching current data for {ticker}...")
    current_data = get_current_data(conn, ticker)
    if not current_data.empty:
        print(f"Current data for {ticker}:")
        print(current_data.head())
    else:
        print(f"No current data found for {ticker}")

    conn.close()