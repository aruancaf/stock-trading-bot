import scraper
import threading
import time
from datetime import datetime
import constants as const
import alpaca as alp
import news
import stock_analysis as sa
import stock_data_gatherer as sdg
import util
import news_classifier as nc
import requests
import datetime as dt
import logging
import backtester as bt

# Configure logging
logging.basicConfig(filename='trading_bot.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def daytrading_stock_analyzer(stocks):
    for stock_ticker in stocks:
        try:
            stock_score = 0
            stock_score += sa.moving_average_checker(stock_ticker)
            stock_score += sa.volume_checker(stock_ticker)
            stock_score += sa.trix_checker(stock_ticker)
            stock_score += sa.aroon_checker(stock_ticker)
            stock_score += sa.elder_ray_checker(stock_ticker)

            if stock_score >= 0.5 and stock_ticker not in day_trading_positions.keys():
                alpaca.create_order(stock_ticker, 1)
                active_positions_to_check[stock_ticker] = ('day_trade', sdg.get_current_stock_data(stock_ticker)['Close'])
                day_trading_positions[stock_ticker] = sdg.get_current_stock_data(stock_ticker)['Close']
                logging.info(f"Based on daytrading pattern analysis, buying {stock_ticker}, Stock Score: {stock_score}")
        except Exception as e:
            logging.error(f"Error in daytrading_stock_analyzer for {stock_ticker}: {e}")

def news_stock_analyzer(stock_ticker):
    try:
        stock_score = 0
        stock_score += nc.sentiment_analyzer(news.get_news(stock_ticker))
        logging.info(f"{stock_ticker} news score: {stock_score}")
        if stock_score >= 0.35 and stock_ticker not in long_term_positions.keys():
            alpaca.create_order(stock_ticker, 1)
            active_positions_to_check[stock_ticker] = ('long_term', sdg.get_current_stock_data(stock_ticker)['Close'])
            long_term_positions[stock_ticker] = sdg.get_current_stock_data(stock_ticker)['Close']
            logging.info(f"Based on News analysis, buying {stock_ticker}")
    except Exception as e:
        logging.error(f"News analysis not working for {stock_ticker}: {e}")

def stock_position_analyzer():
    while True:
        for position, (type, purchase_price) in active_positions_to_check.items():
            threading.Thread(target=check_perform_sell, args=(position, type, purchase_price)).start()
        active_positions_to_check.clear()

def check_perform_sell(stock_ticker, trade_type, purchase_price):
    while True:
        current_stock_price = sdg.get_current_stock_data(stock_ticker)['Close']
        price_change_percent = util.calculate_price_change(current_stock_price, purchase_price)
        logging.info(f"Checking {stock_ticker} Gains/Losses: {price_change_percent}, Price: ${current_stock_price}")
        if trade_type == 'day_trade':
            if sa.moving_average_checker(stock_ticker) < 0 or price_change_percent <= -const.MAX_STOP_LOSS_PERCENT or sa.volume_checker(stock_ticker) < 0:
                alpaca.sell_position(stock_ticker)
                del day_trading_positions[stock_ticker]
                break
        elif trade_type == 'long_term':
            if price_change_percent >= const.LONG_TERM_PROFIT_TARGET or price_change_percent <= -const.LONG_TERM_STOP_LOSS_PERCENT:
                alpaca.sell_position(stock_ticker)
                del long_term_positions[stock_ticker]
                break

class StrategyRunner:
    def __init__(self):
        self.strategies = {
            "combined_strategy": sa.combined_strategy,
            # Add other strategies if needed
        }

    def run_backtest(self, start_date, end_date, initial_balance):
        backtester = bt.Backtester(start_date, end_date, initial_balance)
        tickers = scraper.active_stocks()  # Pull the symbols from the scraper module
        batches = util.partition_array(tickers, 10)  # Split tickers into batches of 10
        for batch_num, batch in enumerate(batches):
            logging.info(f"Starting backtest for batch {batch_num + 1}/{len(batches)}: {batch}")
            for name, strategy in self.strategies.items():
                backtester.run_strategy(strategy, batch)
                final_balance = backtester.calculate_performance()
                logging.info(f"Final balance for {name} in batch {batch_num + 1}: {final_balance}")
                logging.info(f"Trades executed in batch {batch_num + 1}: {backtester.trades}")
            logging.info(f"Completed backtest for batch {batch_num + 1}/{len(batches)}")

if __name__ == "__main__":
    logging.info("Starting the trading bot")

    # Initializing important stuff
    news = news.NewsGetter()
    alpaca = alp.Alpaca()
    active_positions_to_check = {} # key is stock ticker, value is (trade type, stock purchase price)
    day_trading_positions = {} # key is stock ticker, value is stock purchase price
    long_term_positions = {} # key is stock ticker, value is stock purchase price

    positions = alpaca.get_positions()
    for position in positions: #todo also add orders
        active_positions_to_check[position.symbol] = ('day_trade', float(position.cost_basis)) #assuming initial positions are day trades

    logging.info(f"Currently Purchased: {active_positions_to_check}")
    first_time_run = True

    while True:
        try:
            logging.info("New Iteration of Stock Scanning")
            current_time = datetime.now().strftime("%H:%M")
            if const.STOCK_MARKET_OPEN_TIME < current_time < const.STOCK_MARKET_CLOSE_TIME:
                if first_time_run:
                    threading.Thread(target=stock_position_analyzer).start()
                    first_time_run = False
                active_stocks = scraper.active_stocks()
                partitioned_stocks = util.partition_array(active_stocks, const.STOCK_SCANNER_PARTITION_COUNT)
                for partition in partitioned_stocks:
                    threading.Thread(target=daytrading_stock_analyzer, args=[partition]).start()
            else:
                alpaca.sell_all_positions()
                logging.info("Market Close")
                for stock_ticker in const.STOCKS_TO_CHECK: #purchases stocks based on news info
                    threading.Thread(target=news_stock_analyzer, args=(stock_ticker,)).start()

                logging.info("Starting Backtester")
                strategy_runner = StrategyRunner()
                strategy_runner.run_backtest(start_date="2019-01-01", end_date="2023-12-31", initial_balance=1000)
                time.sleep(3600)  # Wait for an hour before checking again
        except Exception as e:
            logging.error(f"Restarting due to error: {e}")

