import stock_data_gatherer as sdg


def moving_average_checker() -> int:
   stock_status = sdg.get_current_stock_data()
   if stock_status['Close'] > stock_status['EMA'] and stock_status['Close'] < stock_status['PREV_SMA'] :
       return 0.3
   else if stock_status['Close'] < stock_status['EMA'] and stock_status['Close'] > stock_status['PREV_SMA'] :
       return -0.3
