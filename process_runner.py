import time

import trading_strategies
import yf_web_scraper
from utils import alerts, multithreading, json_simplifier

#todo: fix
portfolio_manager_test = json_simplifier.PortfolioManager()
while True:
    print("")
    most_active_stocks = yf_web_scraper.get_most_actives()
    print("Position Polarity : {0}".format(portfolio_manager_test.get_position_polarity()))
    print("")

    multithreading.runChunkedThreads(most_active_stocks, trading_strategies.trend_following, 15)

    alerts.sayBeep(3)

    # time.sleep(3)
    #
    # for stk in portfolio_manager_test.stocks['Purchased']:
    #     json_simplifier.sellStock(stk)
    #     time.sleep(2)
