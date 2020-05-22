import os
import threading
from collections import Counter
from datetime import datetime

import yfinance as yf

import trading_constants
import trading_strategies
import yf_web_scraper
from portfolio_manager import PortfolioManager
from utils import json_simplifier, alerts, multithreading

while True:
    most_active_stocks = yf_web_scraper.get_most_actives()
    print("Position Polarity : {0}".format(PortfolioManager().get_position_polarity()))
    print(most_active_stocks)
    json_simplifier.addYFTickerToJson("stock_portfolio.json", yf.Ticker("APPN"), trading_constants.lock, 'Purchased')
    current_price = yf.Ticker("APPN").history("1d").iloc[0]
    buy_price = json_simplifier.delFromJsonReturnDict("stock_portfolio.json", yf.Ticker("APPN"), trading_constants.lock, 'Purchased')
    del current_price['Dividends']
    del current_price['Stock Splits']
    del buy_price['Time']
    print(current_price.to_dict())
    print(buy_price)
    current_price_counter = Counter(current_price.to_dict())
    buy_price_counter = Counter(buy_price)
    print("subtraction")
    current_price_counter.subtract(buy_price_counter)
    print(current_price_counter)
    json_simplifier.addDictToJson("stock_portfolio.json", "APPN",  current_price_counter, trading_constants.lock, 'Sold')
    multithreading.runChunkedThreads(most_active_stocks, trading_strategies.trend_following, 12)
    # json_simplifier.addToJson("stock_portfolio.json", yf.Ticker("AAPL"), trading_constants.lock, 'Purchased')
    # json_simplifier.delFromJson("stock_portfolio.json", yf.Ticker("APPN"), trading_constants.lock, 'Purchased')
    # json_simplifier.addToJson("stock_portfolio.json", yf.Ticker("APPN"), trading_constants.lock, 'Sold')

    alerts.sayBeep(3)

