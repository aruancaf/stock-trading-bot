import yfinance as yf

import yf_extender
import yf_web_scraper
import json
import thread6


def purchase_stocks():
    stocks = {}
    while True:
        most_active_stocks = yf_web_scraper.get_most_actives()
        for stk in most_active_stocks:
            ticker_stock = yf.Ticker(stk)
            stk_price = ticker_stock.history("1d").iloc[0]

            # get stock info
            print("{0} price: {1}".format(stk, stk_price['Close']))
            previous_2mo_high = yf_extender.previous_2mo_high(ticker_stock)
            print("Previous2MoHigh: {0} CurrentStockPrice: {1} ".format(previous_2mo_high, stk_price['Close']))
            # add check?  (stk_price['High'] - stk_price['Close'])/stk_price['High'] < 0.2
            if previous_2mo_high < stk_price['Close'] and (stk_price['High'] - stk_price['Close']) < 0.15:
                print("Buying {0}".format(stk))
                if stk not in stocks:
                    with open("stock_portfolio.json", "r+") as file:
                        stocks = json.load(file)
                        stk_history = ticker_stock.history("1d").iloc[0].to_dict()
                        stocks.update({stk: stk_history})
                        file.seek(0)
                        json.dump(stocks, file, indent=4)


thread6.run_threaded(purchase_stocks())
