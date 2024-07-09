#! ./venv/bin/python3.8

import portfolio_manager
import trading_strategies
import web
import yf_web_scraper
from utils import multithreading
import trading_constants as const

first_run = True
portfolio_manager.initializeApAccount()
portfolio_manager.refresh_account_balance()
multithreading.run_thread(web.init_web)

while True:
    most_active_stocks = const.whitelist + yf_web_scraper.get_active_tickers()
    print(most_active_stocks)
    portfolio_manager.print_account_status()
    if first_run is True:
        multithreading.run_thread(trading_strategies.evaluate_purchased_stocks)
        first_run = False
    multithreading.run_chunked_threads(most_active_stocks, trading_strategies.run_stock_pipelines,
                                       const.trading_strategy_thread_count)

