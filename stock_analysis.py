import stock_data_gatherer as sdg


def moving_average_checker(ticker_symbol) -> int:
   stock_status = sdg.get_current_stock_data(ticker_symbol)
   if stock_status['Close'] > stock_status['EMA'] and stock_status['PREVPRICE'] < stock_status['PREVSMA']:
       return 0.3
   elif stock_status['Close'] < stock_status['SMA'] and stock_status['PREVPRICE'] > stock_status['PREVSMA']:
       return -0.3
   return 0

def volume_checker(ticker_symbol) -> int:
    stock_status = sdg.get_current_stock_data(ticker_symbol)
    try:
        volume =  sdg.get_volume_slope(ticker_symbol)/(0.2*stock_status['Volume'])
    except ZeroDivisionError:
        volume = 0
    try:
        price = sdg.get_price_slope(ticker_symbol)/(0.2*stock_status['Close'])
    except ZeroDivisionError:
        price = 0


    print(ticker_symbol, ": Price: ", price, " Volume: ", volume)
    if price > 0.04 and volume > 1:
        return 0.2
    elif price < -0.03 and volume > 0.8:
        return -0.2
    return 0


