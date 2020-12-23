import scraper
import threading
import time
from datetime import datetime
import constants as const
import alpaca as alp
import stock_analysis as sa
import stock_data_gatherer as sdg
import util


def stock_analyzer(stocks):
    for stock_ticker in stocks:
        if stock_ticker not in all_active_positions.keys():
            stock_score = 0
            print("Analyzing", stock_ticker)
            stock_score += sa.moving_average_checker(stock_ticker)
            if stock_score >= 0.3:
                alpaca.create_order(stock_ticker, 1) #todo: calculate order amount
                active_positions_to_check[stock_ticker] = sdg.get_current_stock_data(stock_ticker)['Close']
                all_active_positions[stock_ticker] = sdg.get_current_stock_data(stock_ticker)['Close']

def stock_position_analyzer():
    while True:
        for position in active_positions_to_check.keys():
            threading.Thread(target=check_perform_sell, args=(position, active_positions_to_check[position])).start()
        active_positions_to_check.clear()



def check_perform_sell(stock_ticker, purchase_price):
    while True:
        current_stock_price = sdg.get_current_stock_data(stock_ticker)['Close']
        price_change_percent = util.calculate_price_change(current_stock_price, all_active_positions[stock_ticker])
        print("Checking", stock_ticker, "Gains/Losses", price_change_percent, "Price: $", current_stock_price) 
        if sa.moving_average_checker(stock_ticker) < 0 or price_change_percent <= -const.MAX_STOP_LOSS_PERCENT:
            alpaca.sell_position(stock_ticker)
            del all_active_positions[stock_ticker]


if __name__ == "__main__":

    #Initializing important stuff

    alpaca = alp.Alpaca()
    active_positions_to_check = {} # key is stock ticker, value is stock purchase price 
    all_active_positions = {} # key is stock ticker, value is stock purchase price 
    positions = alpaca.get_positions()
    for position in positions:
        active_positions_to_check[position.symbol] = float(position.cost_basis)

    all_active_positions = active_positions_to_check.copy()
    print("Currently Purchased:", active_positions_to_check)

    time.sleep(2)
    first_time_run = True
    
    while True:
        current_time = datetime.now().strftime("%H:%M")
        if current_time > const.STOCK_MARKET_OPEN_TIME and current_time < const.STOCK_MARKET_CLOSE_TIME:
            if first_time_run:
                threading.Thread(target=stock_position_analyzer).start()
                first_time_run = False
            active_stocks = scraper.active_stocks()
            partitioned_stocks = util.partition_array(active_stocks, const.STOCK_SCANNER_PARTITION_COUNT)
            for partition in partitioned_stocks:
                threading.Thread(target=stock_analyzer, args=[partition]).start()

        else:
            print("Market Close")
            alpaca.sell_all_positions()
            time.sleep(3600)


