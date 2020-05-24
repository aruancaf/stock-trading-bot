import yfinance as yf


def get_ticker_symbol(ticker: yf.Ticker) -> str:
    return ticker.get_info()['symbol']


def get_stock_info(ticker: yf.Ticker) -> {}:
    stock_info = ticker.history("1d").iloc[0].to_dict()
    del stock_info['Dividends']
    del stock_info['Stock Splits']
    return stock_info


# Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
def get_stock_history(ticker: yf.Ticker, time_period: str):
    stock_history = ticker.history(time_period).values.tolist()
    for i in range(0, len(stock_history)):
        del stock_history[i][4]
        del stock_history[i][5]
    return stock_history


# Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
def previous_high(ticker: yf.Ticker, time_period: str) -> float:
    high = 0
    for i in range(0, len(ticker.history(time_period)) - 2):
        temp_high = ticker.history(time_period).iloc[i]['High']
        if temp_high > high:
            high = temp_high
    return high


# Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
def calculate_sma(ticker: yf.Ticker, time_period="1mo") -> float:
    stock_history = get_stock_history(ticker, time_period)
    summation = 0
    time_period_days = 0
    for i in stock_history:
        summation += i[3]
        time_period_days += 1
    return summation / time_period_days


# Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
def calculate_ema(ticker: yf.Ticker, time_period="1mo") -> float:
    stock_history = get_stock_history(ticker, time_period)
    return get_stock_info(ticker)['Close'] * (2 / (1 + len(stock_history))) + calculate_sma(ticker, time_period) * (
                1 - (2 / (1 + len(stock_history))))
