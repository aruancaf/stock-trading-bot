import json

import yfinance as yf
from thread6 import thread6

import portfolio_manager
import trading_strategies
import yf_web_scraper

with open('stock_portfolio.json', "r+") as file:
    portfolio_manager.stocks = json.load(file)
positionPolarity = 0
for i in portfolio_manager.stocks:
    print("{0} {1}".format(i, yf.Ticker(i).history("1d").iloc[0]['Close'] - portfolio_manager.stocks[i]['Close']))
    positionPolarity += yf.Ticker(i).history("1d").iloc[0]['Close'] - portfolio_manager.stocks[i]['Close']
print("Position Polarity : {0}".format(positionPolarity))
while True:
    most_active_stocks = yf_web_scraper.get_most_actives()
    thread6.run_threaded(trading_strategies.trend_following, most_active_stocks[0:round(len(most_active_stocks) / 4)])
    thread6.run_threaded(trading_strategies.trend_following,
                         most_active_stocks[round(len(most_active_stocks) / 4 + 1): round(len(most_active_stocks) / 2)])
    thread6.run_threaded(trading_strategies.trend_following, most_active_stocks[
                                                             round(len(most_active_stocks) / 2 + 1): round(
                                                                 3 * len(most_active_stocks) / 4)])
    thread6.run_threaded(trading_strategies.trend_following,
                         most_active_stocks[round(3 * len(most_active_stocks) / 4 + 1):len(most_active_stocks)])
