import scraper
import threading
import time
from datetime import datetime
import constants as const
import alpaca as alp
import stock_analysis as sa
import stock_data_gatherer as sdg

alpaca = alp.Alpaca()

time = datetime.now().strftime("%H:%M")
active_positions_to_check = {'AAPL':1000, 'TSLA':1000} # key is stock ticker, value is stock purchase price 
#todo: make this auto update

def stock_analyzer():
    while True:
        active_stocks = scraper.active_stocks()
        stock_score = 0
        for stock_ticker in active_stocks:
            print("Analyzing", stock_ticker)
            stock_score += sa.moving_average_checker(stock_ticker)
            if stock_score > 0.7:
                alpaca.create_order(stock_ticker, 1)
                active_positions_to_check[stock_ticker] = sdg.get_current_stock_data(stock_ticker)['Close']

def stock_position_analyzer():
    for position in active_positions_to_check.keys():
        threading.Thread(check_perform_sell(position, active_positions_to_check[position]))
    active_positions_to_check.clear()



def check_perform_sell(stock_ticker, purchase_price):
    print("Checking", stock_ticker, "Purchase Price", purchase_price)
    if sa.moving_average_checker(stock_ticker) < 0 or purchase_price > (sdg.get_current_stock_data(stock_ticker)['Close'] - const.MAX_STOP_LOSS): #fix max stop loss based on quantity
        alpaca.sell_position(stock_ticker)

runOnce = True
# time = "12:01"
while True:
    if time > const.STOCK_MARKET_OPEN_TIME and time < const.STOCK_MARKET_CLOSE_TIME:
        print("Market Open")
        stock_position_analyzer() # todo: arent running simulataneously
        if runOnce:
            threading.Thread(stock_analyzer())
            runOnce = False
    else:
        print("Market Close")
        alpaca.sell_all_positions()
        time.sleep(3600)


