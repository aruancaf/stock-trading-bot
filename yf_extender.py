import yfinance as yf


def previous_2mo_high(ticker: yf.Ticker) -> int:
    high = ticker.history("2d").iloc[0]['High']
    for i in range(0, len(ticker.history("2mo")) - 2):
        temp_high = ticker.history("2mo").iloc[i]['High']
        if temp_high > high:
            high = temp_high
    return high


def get_ticker_symbol(ticker: yf.Ticker) -> str:
    return ticker.get_info()['symbol']


def get_stock_info(ticker: yf.Ticker) -> {}:
    stock_info = ticker.history("1d").iloc[0].to_dict()
    del stock_info['Dividends']
    del stock_info['Stock Splits']
    return stock_info
