import json
import os
from datetime import datetime
from thread6 import thread6
from portfolio_manager import PortfolioManager
from threading import Lock


def addToJson(fileName, ticker_stock, lock):
    stk = ticker_stock.get_info()['symbol']
    if stk not in PortfolioManager.stocks:
        print("Buying {0}".format(stk))
        os.system("say beep")
        with lock, open(fileName, "r+") as file:
            stk_history = ticker_stock.history("1d").iloc[0].to_dict()
            del stk_history['Dividends']
            del stk_history['Stock Splits']
            stk_history['Time'] = datetime.now().strftime("%H:%M:%S")
            PortfolioManager.stocks.update({stk: stk_history})
            file.seek(0)
            json.dump(PortfolioManager.stocks, file, indent=4)


def readJson(fileName) -> None:
    with open(fileName, "r+") as file:
        PortfolioManager.stocks = json.load(file)
