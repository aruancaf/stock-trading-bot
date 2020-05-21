import time
from datetime import datetime

import yfinance as yf

import trading_constants
import yf_extender
from utils import json_simplifier


def trend_following(stock_database: [str]):
    for stk in stock_database:
        try:
            ticker_stock = yf.Ticker(stk)
            stk_price = ticker_stock.history("1d").iloc[0]

            # get stock info
            print("{0} price: {1} at {2}".format(stk, stk_price['Close'], datetime.now().strftime("%H:%M:%S")))
            previous_2mo_high = yf_extender.previous_2mo_high(ticker_stock)
            # print("Previous2MoHigh: {0} CurrentStockPrice: {1} ".format(previous_2mo_high, stk_price['Close']))

            #  and (stk_price['High'] - stk_price['Close']) < 0.15
            if previous_2mo_high < stk_price['Close'] and (stk_price['High'] - stk_price['Close']) < 0.05:
                json_simplifier.addToJson("stock_portfolio.json", ticker_stock, trading_constants.lock)
            time.sleep(0.05)
        except IndexError:
            print("No Data")

# def checkSell():
#     json_simplifier.readJson()
#         for stk in PortfolioManager.stocks:
#             ticker_stock = yf.Ticker(stk)
#             stk_price = ticker_stock.history("1d").iloc[0]
