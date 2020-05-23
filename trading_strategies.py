import sys
import time
from datetime import datetime

import yfinance as yf

import portfolio_manager
import yf_extender


def trend_following(stock_database: [str]):
    for stk in stock_database:
        try:
            ticker_stock = yf.Ticker(stk)
            stock_info = yf_extender.get_stock_info(ticker_stock)
            print("{0} price: {1} at {2}".format(stk, stock_info['Close'], datetime.now().strftime("%H:%M:%S")))
            sys.stdout.flush()
            previous_2mo_high = yf_extender.previous_2mo_high(ticker_stock)
            if previous_2mo_high < stock_info['Close'] and (stock_info['High'] - stock_info['Close']) < 0.05:
                portfolio_manager.buy_stock(ticker_stock)
            time.sleep(0.1)
        except IndexError:
            print("No Data")
    return True
