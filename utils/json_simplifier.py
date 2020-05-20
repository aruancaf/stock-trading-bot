import json


def addToJson(fileName, ticker_stock, stocks):
    stk = ticker_stock.get_info()['symbol']
    if stk not in stocks:
        with open(fileName, "r+") as file:
            stocks = json.load(file)
            stk_history = ticker_stock.history("1d").iloc[0].to_dict()
            del stk_history['Dividends']
            del stk_history['Stock Splits']
            stocks.update({stk: stk_history})
            file.seek(0)
            json.dump(stocks, file, indent=4)
