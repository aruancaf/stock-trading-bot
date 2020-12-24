import scraper
import threading
import time
from datetime import datetime
import constants as const
import alpaca as alp
import news
import stock_analysis as sa
import stock_data_gatherer as sdg
import util
import news_classifier as nc
import requests

def daytrading_stock_analyzer(stocks):
    for stock_ticker in stocks: #purchases stocks based on daytrading patterns
        try:
            stock_score = 0
            print("Analyzing", stock_ticker)
            stock_score += sa.moving_average_checker(stock_ticker)
            if stock_score >= 0.3 and stock_ticker not in all_active_positions.keys():
                alpaca.create_order(stock_ticker, 1) #todo: calculate order amount
                active_positions_to_check[stock_ticker] = sdg.get_current_stock_data(stock_ticker)['Close']
                all_active_positions[stock_ticker] = sdg.get_current_stock_data(stock_ticker)['Close']
                print("Based on daytrading pattern analysis, buying", stock_ticker)
        except Exception as e:
            pass

def news_stock_analyzer(stock_ticker):
    stock_score = 0
    stock_score += nc.sentiment_analyzer(news.get_news(stock_ticker))
    print(stock_ticker, "news score:", stock_score)
    if stock_score >= 0.35 and stock_ticker not in all_active_positions.keys():
        alpaca.create_order(stock_ticker, 1) #todo: calculate order amount
        active_positions_to_check[stock_ticker] = sdg.get_current_stock_data(stock_ticker)['Close']
        all_active_positions[stock_ticker] = sdg.get_current_stock_data(stock_ticker)['Close']
        print("Based on News analysis, buying", stock_ticker)


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
            break


if __name__ == "__main__":

    #Initializing important stuff
    news = news.NewsGetter()
    alpaca = alp.Alpaca()
    active_positions_to_check = {} # key is stock ticker, value is stock purchase price 
    all_active_positions = {} # key is stock ticker, value is stock purchase price 
    positions = alpaca.get_positions()
    for position in positions: #todo also add orders
        active_positions_to_check[position.symbol] = float(position.cost_basis) #cost basis not working well
                                                                                # rescanning of stocks is breaking system

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
                threading.Thread(target=daytrading_stock_analyzer, args=[partition]).start()

            for stock_ticker in const.STOCKS_TO_CHECK: #purchases stocks based on news info
                threading.Thread(target=news_stock_analyzer, args=(stock_ticker,)).start()

        else:
            print("Market Close")
            alpaca.sell_all_positions()
            time.sleep(3600)


