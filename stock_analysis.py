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
    print(ticker_symbol, ": Price: ", sdg.get_price_slope(ticker_symbol)/(0.2*stock_status['Close']), " Volume: ", sdg.get_volume_slope(ticker_symbol)/(0.2*stock_status['Volume']))
    if sdg.get_price_slope(ticker_symbol)/(0.2*stock_status['Close']) > 0.04 and sdg.get_volume_slope(ticker_symbol)/(0.2*stock_status['Volume']) > 1:
        return 0.2
    elif sdg.get_price_slope(ticker_symbol)/(0.2*stock_status['Close']) < -0.03 and sdg.get_volume_slope(ticker_symbol)/(0.2*stock_status['Volume']) > 0.8:
        return -0.2
    return 0


