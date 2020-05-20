import yfinance as yf

import yf_extender
import yf_web_scraper

while True:
    for stk in yf_web_scraper.get_most_actives():
        ticker_stock = yf.Ticker(stk)
        stk_price = ticker_stock.history("1d").iloc[0]['Close']
        #     get stock info
        print("{0} price: {1}".format(stk, stk_price))
        previous_2mo_high = yf_extender.previous_2mo_high(ticker_stock)
        print("Previous2MoHigh: {0} CurrentStockPrice: {1} ".format(previous_2mo_high, stk_price))
        if previous_2mo_high < stk_price:
            print(ticker_stock.get_info())
            print("buy!!!!")
