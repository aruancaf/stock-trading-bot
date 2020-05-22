import json
import os
import sys
import threading
from collections import Counter
from datetime import datetime

import yfinance as yf

import trading_constants
from portfolio_manager import PortfolioManager
from utils import alerts


def addYFTickerToJson(fileName: str, ticker_stock: yf.Ticker, lock: threading.Lock, category: str):
    stk = ticker_stock.get_info()['symbol']
    if stk not in PortfolioManager.stocks[category]:
        print("Buying {0}".format(stk))
        sys.stdout.flush()
        alerts.sayBeep(1)
        with lock, open(fileName, "r+") as file:
            stk_history = ticker_stock.history("1d").iloc[0].to_dict()
            del stk_history['Dividends']
            del stk_history['Stock Splits']
            stk_history['Time'] = datetime.now().strftime("%H:%M:%S")
            PortfolioManager.stocks[category].update({stk: stk_history})
            file.seek(0)
            json.dump(PortfolioManager.stocks, file, indent=4)
            return ticker_stock
    else:
        return None


def addDictToJson(fileName: str, stock_name: str, ticker_stock, lock: threading.Lock, category: str):
    if stock_name not in PortfolioManager.stocks[category]:
        print("Buying {0}".format(stock_name))
        alerts.sayBeep(1)
        with lock, open(fileName, "r+") as file:

            PortfolioManager.stocks[category].update({stock_name: ticker_stock})
            file.seek(0)
            json.dump(PortfolioManager.stocks, file, indent=4)
            return ticker_stock
    else:
        return None


def readJson(fileName: str) -> None:
    with open(fileName, "r+") as file:
        PortfolioManager.stocks = json.load(file)


def delFromJson(delFrom: str, ticker_stock: yf.Ticker, lock: threading.Lock, category: str) -> yf.Ticker:
    stk = ticker_stock.get_info()['symbol']
    readJson(delFrom)
    if stk in PortfolioManager.stocks[category]:
        os.system("say beep")
        os.system("say beep")
        with lock, open(delFrom, "r+") as file:
            stk_history = ticker_stock.history("1d").iloc[0].to_dict()
            del stk_history['Dividends']
            del stk_history['Stock Splits']
            stk_history['Time'] = datetime.now().strftime("%H:%M:%S")
            del PortfolioManager.stocks[category][stk]
            file.seek(0)
            file.truncate(0)
            json.dump(PortfolioManager.stocks, file, indent=4)
            return ticker_stock
    else:
        return None


def delFromJsonReturnDict(delFrom: str, ticker_stock: yf.Ticker, lock: threading.Lock, category: str):
    stk = ticker_stock.get_info()['symbol']
    readJson(delFrom)
    if stk in PortfolioManager.stocks[category]:
        os.system("say beep")
        os.system("say beep")
        with lock, open(delFrom, "r+") as file:
            print("Selling {0}".format(stk))
            stk_history = ticker_stock.history("1d").iloc[0].to_dict()
            del stk_history['Dividends']
            del stk_history['Stock Splits']
            stk_history['Time'] = datetime.now().strftime("%H:%M:%S")
            temp = PortfolioManager.stocks[category][stk]
            del PortfolioManager.stocks[category][stk]
            file.seek(0)
            file.truncate(0)
            json.dump(PortfolioManager.stocks, file, indent=4)
            return temp
    else:
        return None


def sellStock(ticker_name: str):
    addYFTickerToJson("stock_portfolio.json", yf.Ticker(ticker_name), trading_constants.lock, 'Purchased')
    current_price = yf.Ticker(ticker_name).history("1d").iloc[0]
    buy_price = delFromJsonReturnDict("stock_portfolio.json", yf.Ticker(ticker_name), trading_constants.lock,
                                      'Purchased')
    del current_price['Dividends']
    del current_price['Stock Splits']
    del buy_price['Time']
    current_price_counter = Counter(current_price.to_dict())
    buy_price_counter = Counter(buy_price)
    current_price_counter.subtract(buy_price_counter)
    print(current_price_counter)
    addDictToJson("stock_portfolio.json", ticker_name, current_price_counter, trading_constants.lock, 'Sold')
