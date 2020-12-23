import yfinance as yf
import calculation

# @param ticker_symbol - str
# @param time_period - Valid Periods: 1d, 5d, 1mo,3mo,6mo,1y,2y,5y,10y,ytd,maxi
# @param time_interval - Valid Periods:`1m , 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
def get_historical_data(ticker_symbol: str, time_period: str, time_interval: str) -> yf.Ticker:
    return yf.Ticker(ticker_symbol).history(period=time_period, interval=time_interval)

#todo: check all is functional
def get_current_stock_data(ticker_symbol: str) -> {}:
    historical_stock_data = get_historical_data(ticker_symbol, '3d', '2m')
    stock_data = historical_stock_data.iloc[0].to_dict()
    
    del stock_data['Dividends']
    del stock_data['Stock Splits']

    stock_data['SMA'] = calculation.calculate_sma(historical_stock_data)[0]
    stock_data['PREVSMA'] = calculation.calculate_sma(historical_stock_data)[1]
    stock_data['EMA'] = calculation.calculate_ema(historical_stock_data)
    stock_data['PREVPRICE'] = historical_stock_data.iloc[2].to_dict()['Close']

    return stock_data


def get_stock_company_name(ticker_symbol:str):
    return yf.Ticker(ticker_symbol).info['shortName']
