from collections import Counter
from datetime import datetime

import yfinance as yf

import yf_extender
from utils import json_simplifier
import portfolio_manager

stocks = {"Purchased": {}, "Sold": {}}


def get_position_polarity() -> float:
    position_polarity = 0
    portfolio_manager.stocks = json_simplifier.readJson('stock_portfolio.json')
    ticker_changes = []
    for i in stocks['Purchased']:
        polarity_stock = yf_extender.get_stock_info(yf.Ticker(i))['Close'] - stocks['Purchased'][i]['Close']
        ticker_changes.append("{0} {1}".format(i, polarity_stock))
        position_polarity += polarity_stock

    print("Position Polarity : {0}".format(position_polarity))
    print(ticker_changes)
    return position_polarity


def buy_stock(ticker: yf.Ticker):
    json_simplifier.addYFTickerToJson('stock_portfolio.json', ticker, 'Purchased')
    print("Buying {0}".format(ticker.get_info()['symbol']))


def sell_stock(ticker: yf.Ticker):
    stock_info = yf_extender.get_stock_info(ticker)

    purchased_stock_info = json_simplifier.delFromJsonReturnDict("stock_portfolio.json", ticker,
                                                                 'Purchased')

    del purchased_stock_info['Time']
    stock_price_counter = Counter(stock_info)
    purchased_stock_counter = Counter(purchased_stock_info)
    stock_price_counter.subtract(purchased_stock_counter)
    stock_price_counter['Time'] = datetime.now().strftime("%H:%M:%S")
    json_simplifier.addDictToJson("stock_portfolio.json", ticker, stock_price_counter,
                                  'Sold')
    print("Selling {0}".format(ticker.get_info()['symbol']))
