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

