import portfolio_manager
import trading_strategies
import web
import yf_web_scraper
from utils import multithreading
import trading_constants as const
import backtester
import logging
import time

# Initialize and refresh the portfolio
first_run = True
portfolio_manager.initializeApAccount()
portfolio_manager.refresh_account_balance()
multithreading.run_thread(web.init_web)

# Define the backtesting function
def run_backtests():
    # Define the start and end dates for the backtest
    start_date = "2019-01-01"
    end_date = "2023-12-31"
    initial_balance = 1000

    strategy_runner = backtester.StrategyRunner()
    strategy_metrics = strategy_runner.run_backtest(start_date, end_date, initial_balance)
    
    # Log the backtest results
    for strategy, metrics in strategy_metrics.items():
        print(f"Strategy: {strategy}")
        for metric, value in metrics.items():
            print(f"{metric}: {value}")
        print("\n")

# Main loop
while True:
    try:
        most_active_stocks = const.whitelist + yf_web_scraper.get_active_tickers()
        print(most_active_stocks)
        portfolio_manager.print_account_status()
        
        if first_run:
            multithreading.run_thread(trading_strategies.evaluate_purchased_stocks)
            first_run = False

        multithreading.run_chunked_threads(most_active_stocks, trading_strategies.run_stock_pipelines,
                                           const.trading_strategy_thread_count)
        
        # Run backtests after all other tasks
        run_backtests()

        # Sleep for a specified interval before the next iteration
        time.sleep(const.MAIN_LOOP_INTERVAL)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        time.sleep(60)  # Wait for a minute before retrying in case of an error