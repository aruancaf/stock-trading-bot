import yfinance as yf

def fetch_yahoo_finance_data(symbol: str, period: str = '1y', interval: str = '1d'):
    # Fetch historical data
    ticker = yf.Ticker(symbol)
    historical_data = ticker.history(period=period, interval=interval)
    
    # Fetch current data
    current_data = ticker.info

    # Display the historical data columns and some sample data
    print(f"Historical data columns for {symbol}: {historical_data.columns}")
    print(historical_data.head())

    # Display the current data keys and some sample data
    print(f"\nCurrent data keys for {symbol}: {list(current_data.keys())}")
    for key, value in current_data.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    ticker_symbol = 'AAPL'  # Example ticker symbol
    fetch_yahoo_finance_data(ticker_symbol)