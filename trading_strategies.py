import json
from datetime import datetime

import yfinance as yf

import portfolio_manager
import yf_extender
from utils import json_simplifier


def trend_following(stock_database):
    for stk in stock_database:
        ticker_stock = yf.Ticker(stk)
        stk_price = ticker_stock.history("1d").iloc[0]
        current_time = datetime.now().time()

        # get stock info
        print("{0} price: {1} at {2}".format(stk, stk_price['Close'], current_time))
        previous_2mo_high = yf_extender.previous_2mo_high(ticker_stock)
        print("Previous2MoHigh: {0} CurrentStockPrice: {1} ".format(previous_2mo_high, stk_price['Close']))

        #  and (stk_price['High'] - stk_price['Close']) < 0.15
        if previous_2mo_high < stk_price['Close'] and (stk_price['High'] - stk_price['Close']) < 0.15:
            print("Buying {0}".format(stk))
            json_simplifier.addToJson("stock_portfolio.json", ticker_stock, portfolio_manager.stocks)


def checkSell():
    with open("stock_portfolio.json", "r+") as file:
        stocks = json.load(file)
        for stk in stocks:
            ticker_stock = yf.Ticker(stk)
            stk_price = ticker_stock.history("1d").iloc[0]
            # if ()
