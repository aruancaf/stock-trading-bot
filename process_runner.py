import threading

import trading_strategies
import yf_web_scraper
from portfolio_manager import PortfolioManager

print("Position Polarity : {0}".format(PortfolioManager().get_position_polarity()))

while True:
    most_active_stocks = yf_web_scraper.get_most_actives()
    print(most_active_stocks)
    thread1 = threading.Thread(target=trading_strategies.trend_following, args=[most_active_stocks])
    thread2 = threading.Thread(target=trading_strategies.trend_following,
                               args=[most_active_stocks[0:round(len(most_active_stocks) / 4)]])
    thread3 = threading.Thread(target=trading_strategies.trend_following,
                               args=[most_active_stocks[
                                     round(len(most_active_stocks) / 4 + 1): round(len(most_active_stocks) / 2)]])
    thread1.start()

    thread2.start()

    thread3.start()
    # thread6.run_threaded(trading_strategies.trend_following, most_active_stocks[
    #                                                          round(len(most_active_stocks) / 2 + 1): round(
    #                                                              3 * len(most_active_stocks) / 4)])
    # thread6.run_threaded(trading_strategies.trend_following,
    #                      most_active_stocks[round(3 * len(most_active_stocks) / 4 + 1):len(most_active_stocks)])
