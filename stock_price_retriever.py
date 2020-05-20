import yfinance as yf
import yf_web_scraper

for stk in yf_web_scraper.get_most_actives():
    stock_info = yf.Ticker(stk)

    # get stock info
    print("{0} price: {1}".format(stk, stock_info.history("1d").iloc[0]['Close']))
