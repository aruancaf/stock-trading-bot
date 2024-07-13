import threading
import time
from datetime import datetime
import logging
from diskcache import Cache
import constants as const
import scraper
import stock_analysis as sa
import stock_data_gatherer as sdg
import util
import news_classifier as nc
import alpaca as alp
import news
from db_manager import dbHandler
from dotenv import load_dotenv
import os
import data_middleman as dm

# Load environment variables from .env file
load_dotenv()

# Initialize the lock
db_lock = threading.Lock()
position_lock = threading.Lock()

class StrategyRunner:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.strategies = {
            "combined_strategy": sa.combined_strategy,
            "moving_average_checker": sa.moving_average_checker,
            "volume_checker": sa.volume_checker,
            "trix_checker": sa.trix_checker,
            "aroon_checker": sa.aroon_checker,
            "elder_ray_checker": sa.elder_ray_checker,
            "heikin_ashi_checker": sa.heikin_ashi_checker,
            "rapid_rebound_checker": sa.rapid_rebound_checker,
            "parabolic_sar_checker": sa.parabolic_sar_checker,
        }

    def execute(self, stocks):
        conn = dm.connect_to_db()  # Ensure conn is defined
        for stock_ticker in stocks:
            try:
                stock_info = dm.get_current_data(conn, stock_ticker)
                stock_score = sum(
                    strategy(stock_info, stock_ticker)
                    for strategy_name, strategy in self.strategies.items()
                )
                if stock_score >= 0.5 and stock_ticker not in day_trading_positions:
                    alpaca.create_order(stock_ticker, 1)
                    with position_lock:
                        day_trading_positions[stock_ticker] = stock_info['close']
                        active_positions_to_check[stock_ticker] = ('day_trade', stock_info['close'])

                    order_data = {
                        'ticker': stock_ticker,
                        'order_type': 'buy',
                        'quantity': 1,
                        'price': stock_info['close'],
                        'order_status': 'filled',
                        'timestamp': datetime.now()
                    }
                    with db_lock:
                        self.db_manager.insert_order(order_data)

                    logging.info(f"Based on analysis, buying {stock_ticker}, Stock Score: {stock_score}")
            except Exception as e:
                logging.error(f"Error in StrategyRunner execute: {e}")
        conn.close()  # Close the connection after use

def stock_position_analyzer(db_manager):
    conn = dm.connect_to_db()  # Ensure conn is defined
    while True:
        with position_lock:
            for stock_ticker, (trade_type, purchase_price) in list(active_positions_to_check.items()):
                threading.Thread(target=check_perform_sell, args=(conn, stock_ticker, trade_type, purchase_price, db_manager)).start()
            active_positions_to_check.clear()
        time.sleep(const.ANALYSIS_INTERVAL)
    conn.close()  # Close the connection after use

def should_sell(current_price, purchase_price):
    return_price = (current_price - purchase_price) / purchase_price
    return 0.03 <= return_price <= 0.05

def check_perform_sell(conn, stock_ticker, trade_type, purchase_price, db_manager):
    while True:
        stock_info = dm.get_current_data(conn, stock_ticker)
        current_stock_price = stock_info['close']
        price_change_percent = util.calculate_price_change(current_stock_price, purchase_price)
        logging.info(f"Checking {stock_ticker} Gains/Losses: {price_change_percent:.2%}, Price: ${current_stock_price:.2f}")
        if trade_type == 'day_trade':
            if should_sell(current_stock_price, purchase_price) or sa.moving_average_checker(stock_info, stock_ticker) < 0 or price_change_percent <= -const.MAX_STOP_LOSS_PERCENT or sa.volume_checker(stock_info, stock_ticker) < 0:
                alpaca.sell_position(stock_ticker)
                with position_lock:
                    if stock_ticker in day_trading_positions:
                        del day_trading_positions[stock_ticker]
                    else:
                        logging.warning(f"{stock_ticker} not found in day_trading_positions")
                        continue

                order_data = {
                    'ticker': stock_ticker,
                    'order_type': 'sell',
                    'quantity': 1,
                    'price': current_stock_price,
                    'order_status': 'filled',
                    'timestamp': datetime.now()
                }
                with db_lock:
                    db_manager.insert_order(order_data)

                logging.info(f"Sold {stock_ticker} from day trade at {current_stock_price}")
                break
        elif trade_type == 'long_term':
            if should_sell(current_stock_price, purchase_price) or price_change_percent >= const.LONG_TERM_PROFIT_TARGET or price_change_percent <= -const.LONG_TERM_STOP_LOSS_PERCENT:
                alpaca.sell_position(stock_ticker)
                with position_lock:
                    if stock_ticker in long_term_positions:
                        del long_term_positions[stock_ticker]
                    else:
                        logging.warning(f"{stock_ticker} not found in long_term_positions")
                        continue

                order_data = {
                    'ticker': stock_ticker,
                    'order_type': 'sell',
                    'quantity': 1,
                    'price': current_stock_price,
                    'order_status': 'filled',
                    'timestamp': datetime.now()
                }
                with db_lock:
                    db_manager.insert_order(order_data)

                logging.info(f"Sold {stock_ticker} from long term at {current_stock_price}")
                break
        time.sleep(const.ANALYSIS_INTERVAL)

def news_stock_analyzer(stock_ticker, db_manager):
    conn = dm.connect_to_db()  # Ensure conn is defined
    try:
        stock_info = dm.get_current_data(conn, stock_ticker)
        stock_score = 0
        stock_score += nc.sentiment_analyzer(news.get_news(stock_ticker))
        logging.info(f"{stock_ticker} news score: {stock_score}")
        if stock_score >= 0.35 and stock_ticker not in long_term_positions:
            alpaca.create_order(stock_ticker, 1)
            with position_lock:
                long_term_positions[stock_ticker] = stock_info['close']
                active_positions_to_check[stock_ticker] = ('long_term', stock_info['close'])

            order_data = {
                'ticker': stock_ticker,
                'order_type': 'buy',
                'quantity': 1,
                'price': stock_info['close'],
                'order_status': 'filled',
                'timestamp': datetime.now()
            }
            with db_lock:
                db_manager.insert_order(order_data)

            logging.info(f"Based on News analysis, buying {stock_ticker}")
    except Exception as e:
        logging.error(f"News analysis not working for {stock_ticker}. Error: {e}")
    conn.close()  # Close the connection after use

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting the trading bot")

    # Load DB credentials from .env file
    db_credentials = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT")
    }
    db_manager = dbHandler(db_credentials)

    # Initialize cache
    cache = Cache('./stock_data_cache')

    # Initialize important stuff
    news_getter = news.NewsGetter()
    alpaca = alp.Alpaca()
    day_trading_positions = {}  # key is stock ticker, value is stock purchase price
    long_term_positions = {}  # key is stock ticker, value is stock purchase price
    active_positions_to_check = {}

    conn = dm.connect_to_db()  # Ensure conn is defined
    positions = alpaca.get_positions()
    with position_lock:
        active_positions_to_check = {
            position.symbol: ('day_trade', float(position.cost_basis))
            for position in positions
        }
    logging.info(f"Currently Purchased: {active_positions_to_check}")
    first_time_run = True

    # Use the scrape_all_urls function to get the valid tickers
    valid_tickers = scraper.scrape_all_urls()

    # Store initial stock data in the database
    for ticker in valid_tickers:
        stock_data = sdg.get_current_stock_data(ticker)
        stock_data['price_slope'] = sdg.get_price_slope(ticker)
        stock_data['volume_slope'] = sdg.get_volume_slope(ticker)
        stock_data['company_name'] = sdg.get_stock_company_name(ticker)
        sdg.store_stock_data_in_db(ticker, stock_data)
        logging.info(f"Stored data for {ticker}")

    while True:
        try:
            logging.info("New Iteration of Stock Scanning")
            current_time = datetime.now().strftime("%H:%M")
            if const.STOCK_MARKET_OPEN_TIME < current_time < const.STOCK_MARKET_CLOSE_TIME:
                if first_time_run:
                    threading.Thread(target=stock_position_analyzer, args=(db_manager,)).start()
                    first_time_run = False
                active_stocks = scraper.active_stocks()
                partitioned_stocks = list(util.partition_array(active_stocks, const.STOCK_SCANNER_PARTITION_COUNT))
                for partition in partitioned_stocks:
                    threading.Thread(target=StrategyRunner(db_manager).execute, args=(partition,)).start()
            else:
                logging.info("Market Close")

                # Run the backtester continuously until market opens
                while current_time >= const.STOCK_MARKET_CLOSE_TIME or current_time < const.STOCK_MARKET_OPEN_TIME:
                    logging.info("Starting Backtester")
                    threading.Thread(target=StrategyRunner(db_manager).run_strategy, args=(db_manager,)).start()  # Run backtests after other tasks
                    time.sleep(3600)  # Wait for an hour before running again
                    current_time = datetime.now().strftime("%H:%M")

            # Execute the news analyzer for both constant stocks and active stocks from the scraper module
            for stock_ticker in const.STOCKS_TO_CHECK + scraper.active_stocks():
                threading.Thread(target=news_stock_analyzer, args=(stock_ticker, db_manager)).start()

            logging.info("Starting Backtester")
            threading.Thread(target=StrategyRunner(db_manager).run_strategy, args=(db_manager,)).start()  # Run backtests after other tasks

            logging.info("Finished Backtester")
            time.sleep(14400)  # Wait for 4 hours before running again
        except Exception as e:
            logging.error(f"Restarting due to error: {e}")
            time.sleep(60)  # Wait for a minute before retrying in case of an error

    # Close DB connection and cache on exit
    db_manager.close()
    cache.close()
    conn.close()