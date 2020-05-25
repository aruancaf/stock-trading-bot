import json
import sys
import threading
from datetime import datetime

import yfinance as yf

import portfolio_manager
import yf_extender

lock = threading.Lock()


def addYFTickerToJson(fileName: str, ticker: yf.Ticker, category: str):
    stk = yf_extender.get_ticker_symbol(ticker)
    portfolio_manager.stocks = readJson(fileName)
    if stk not in portfolio_manager.stocks[category]:
        sys.stdout.flush()
        with lock, open(fileName, "r+") as file:
            stock_info = yf_extender.get_stock_info(ticker)
            stock_info['Time'] = datetime.now().strftime("%H:%M:%S")
            portfolio_manager.stocks[category].update({stk: stock_info})
            file.seek(0)
            json.dump(portfolio_manager.stocks, file, indent=4)
            return ticker
    else:
        return None


def addDictToJson(fileName: str, ticker: yf.Ticker, ticker_info, category: str):
    ticker_symbol = yf_extender.get_ticker_symbol(ticker)
    portfolio_manager.stocks = readJson(fileName)
    if ticker_symbol not in portfolio_manager.stocks[category]:
        with lock, open(fileName, "r+") as file:
            portfolio_manager.stocks[category].update({ticker_symbol: ticker_info})
            file.seek(0)
            json.dump(portfolio_manager.stocks, file, indent=4)
            return ticker_symbol
    else:
        return None


def readJson(fileName: str):
    with open(fileName, "r+") as file:
        return json.load(file)


def delFromJson(delFrom: str, ticker: yf.Ticker, category: str) -> yf.Ticker:
    ticker_symbol = yf_extender.get_ticker_symbol(ticker)

    portfolio_manager.stocks = readJson(delFrom)
    if ticker_symbol in portfolio_manager.stocks[category]:
        with lock, open(delFrom, "r+") as file:
            stock_info = yf_extender.get_stock_info(ticker)
            stock_info['Time'] = datetime.now().strftime("%H:%M:%S")
            del portfolio_manager.stocks[category][ticker_symbol]
            file.seek(0)
            file.truncate(0)
            json.dump(portfolio_manager.stocks, file, indent=4)
            return ticker
    else:
        return None


def delFromJsonReturnDict(delFrom: str, ticker: yf.Ticker, category: str):
    ticker_symbol = yf_extender.get_ticker_symbol(ticker)
    portfolio_manager.stocks = readJson(delFrom)

    if ticker_symbol in portfolio_manager.stocks[category]:
        with lock, open(delFrom, "r+") as file:
            stock_info = yf_extender.get_stock_info(ticker)
            stock_info['Time'] = datetime.now().strftime("%H:%M:%S")
            temp = portfolio_manager.stocks[category][ticker_symbol]
            del portfolio_manager.stocks[category][ticker_symbol]
            file.seek(0)
            file.truncate(0)
            json.dump(portfolio_manager.stocks, file, indent=4)
            return temp
