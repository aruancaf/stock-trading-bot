import threading

import trading_strategies
import yf_web_scraper
from portfolio_manager import PortfolioManager


while True:
    most_active_stocks = yf_web_scraper.get_most_actives()
    # print(most_active_stocks)
    print("Position Polarity : {0}".format(PortfolioManager().get_position_polarity()))

    partitioned_most_active_stock = []
    n = 8
    for i in range(0, len(most_active_stocks), n):
        partitioned_most_active_stock.append(most_active_stocks[i:i + n])

    print(partitioned_most_active_stock)

    threads = []

    for partition in partitioned_most_active_stock:
        threads.append(threading.Thread(target=trading_strategies.trend_following,
                                args=[partition]))
    #
    # [threading.Thread(target=trading_strategies.trend_following,
    #                             args=[most_active_stocks[0:round(len(most_active_stocks) / 4)]]),
    #            threading.Thread(target=trading_strategies.trend_following,
    #                             args=[most_active_stocks[
    #                                   round(len(most_active_stocks) / 4 + 1): round(len(most_active_stocks) / 2)]]),
    #            threading.Thread(target=trading_strategies.trend_following, args=[
    #                most_active_stocks[round(3 * len(most_active_stocks) / 4) + 1: len(most_active_stocks)]]),
    #            threading.Thread(target=trading_strategies.trend_following, args=[
    #                most_active_stocks[round(len(most_active_stocks) / 2) + 1: round(3 * len(most_active_stocks) / 4)]])]
    #
    # , threading.Thread(target=trading_strategies.trend_following, args=[most_active_stocks[round(3 * len(most_active_stocks) / 4) + 1: len(most_active_stocks)]])]

    for thread in threads:
        thread.start()

    threads[0].join()

    print("doneeeeeeeeee")

# all(x==thread[0] for x in threads)

