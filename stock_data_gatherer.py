import yfinance as yf
import util

# @param ticker_symbol - str
# @param time_period - Valid Periods: 1d, 5d, 1mo,3mo,6mo,1y,2y,5y,10y,ytd,maxi
# @param time_interval - Valid Periods:`1m , 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
def get_historical_data(ticker_symbol: str, time_period: str, time_interval: str) -> yf.Ticker:
    return yf.Ticker(ticker_symbol).history(period=time_period, interval=time_interval)

#todo: check all is functional
def get_current_stock_data(ticker_symbol: str) -> {}:
    historical_stock_data = get_historical_data(ticker_symbol, '3d', '2m')
    stock_data = historical_stock_data.iloc[-1].to_dict()
    
    del stock_data['Dividends']
    del stock_data['Stock Splits']

    stock_data['SMA'] = util.calculate_sma(historical_stock_data)[0]#method broken because of history access
    stock_data['PREVSMA'] = util.calculate_sma(historical_stock_data)[1]
    stock_data['EMA'] = util.calculate_ema(historical_stock_data)
    stock_data['PREVPRICE'] = historical_stock_data.iloc[-2].to_dict()['Close']#might need to change, only checks price 2 minutes ago

    return stock_data

def get_price_slope(ticker_symbol:str): #refactor maybe
    n = 5 # checks last 3 minutes of data
    historical_stock_data = get_historical_data(ticker_symbol, '1d', '1m')
    stock_price_by_time = []
    for i in range(-n, 0):
        stock_price_by_time.append(historical_stock_data.iloc[i].to_dict()['Close'])
    slope = util.linear_regress_slope(1, stock_price_by_time)
    return slope

def get_volume_slope(ticker_symbol:str): #refactor maybe
    n = 5 # checks last 3 minutes of data
    historical_stock_data = get_historical_data(ticker_symbol, '1d', '1m')
    stock_volume_by_time = []
    for i in range(-n, 0):
        stock_volume_by_time.append(historical_stock_data.iloc[i].to_dict()['Volume'])
    slope = util.linear_regress_slope(1, stock_volume_by_time)
    return slope

def get_stock_company_name(ticker_symbol:str):
    return yf.Ticker(ticker_symbol).info['longName']
