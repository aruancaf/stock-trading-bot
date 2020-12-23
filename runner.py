import scraper
import threading
import time
from datetime import datetime
import constants as const
import alpaca as alp
import stock_analysis as sa
import stock_data_gatherer as sdg
import util

alpaca = alp.Alpaca()

current_time = datetime.now().strftime("%H:%M")
active_positions_to_check = {} # key is stock ticker, value is stock purchase price 

def stock_analyzer(stocks):
    for stock_ticker in stocks:
        stock_score = 0
        print("Analyzing", stock_ticker)
        stock_score += sa.moving_average_checker(stock_ticker)
        if stock_score >= 0.3:
            alpaca.create_order(stock_ticker, 1) #todo: calculate order amount
            active_positions_to_check[stock_ticker] = sdg.get_current_stock_data(stock_ticker)['Close']

def stock_position_analyzer():
    for position in active_positions_to_check.keys():
        threading.Thread(target=check_perform_sell, args=(position, active_positions_to_check[position])).start()
    active_positions_to_check.clear()



def check_perform_sell(stock_ticker, purchase_price):
    print("Checking", stock_ticker, "Purchase Price", purchase_price)
    if sa.moving_average_checker(stock_ticker) < 0 or sa.calculate_price_change(sdg.get_current_stock_data(stock_ticker)['Close'], active_positions_to_check[stock_ticker]) <= -const.MAX_STOP_LOSS_PERCENT:
        alpaca.sell_position(stock_ticker)

while True:
    if current_time > const.STOCK_MARKET_OPEN_TIME and current_time < const.STOCK_MARKET_CLOSE_TIME:
        print("Market Open")
        stock_position_analyzer()
        active_stocks = scraper.active_stocks()
        partitioned_stocks = util.partition_array(active_stocks, const.STOCK_SCANNER_PARTITION_COUNT)
        for partition in partitioned_stocks:
            threading.Thread(target=stock_analyzer, args=[partition]).start()

    else:
        print("Market Close")
        alpaca.sell_all_positions()
        time.sleep(3600)


