import json
import os
from datetime import datetime

import portfolio_manager


def addToJson(fileName, ticker_stock):
    stk = ticker_stock.get_info()['symbol']
    with open(fileName, "r+") as file:
        portfolio_manager.stocks = json.load(file)
    if stk not in portfolio_manager.stocks:
        print("Buying {0}".format(stk))
        os.system("say beep")
        with open(fileName, "r+") as file:
            stk_history = ticker_stock.history("1d").iloc[0].to_dict()
            del stk_history['Dividends']
            del stk_history['Stock Splits']
            stk_history['Time'] = datetime.now().strftime("%H:%M:%S")
            portfolio_manager.stocks.update({stk: stk_history})
            file.seek(0)
            json.dump(portfolio_manager.stocks, file, indent=4)
