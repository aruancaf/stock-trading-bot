import threading
import time
from datetime import datetime
import logging
import constants as const
from process_runner import run_backtests
import scraper
import stock_analysis as sa
import stock_data_gatherer as sdg
import util
import news_classifier as nc
import backtester as bt
import alpaca as alp
import news

# Initialize the lock
position_lock = threading.Lock()

def daytrading_stock_analyzer(stocks):
    for stock_ticker in stocks:
        try:
            stock_info = sdg.get_current_stock_data(stock_ticker)
            stock_score = 0
            stock_score += sa.moving_average_checker(stock_info, stock_ticker)
            stock_score += sa.volume_checker(stock_info, stock_ticker)
            stock_score += sa.trix_checker(stock_info, stock_ticker)
            stock_score += sa.aroon_checker(stock_info, stock_ticker)
            stock_score += sa.elder_ray_checker(stock_info, stock_ticker)
            stock_score += sa.heikin_ashi_checker(stock_info, stock_ticker)
            stock_score += sa.rapid_rebound_checker(stock_info, stock_ticker)
            stock_score += sa.parabolic_sar_checker(stock_info, stock_ticker)
            
            if stock_score >= 0.5 and stock_ticker not in day_trading_positions:
                alpaca.create_order(stock_ticker, 1)
                with position_lock:
                    day_trading_positions[stock_ticker] = stock_info['Close']
                    active_positions_to_check[stock_ticker] = ('day_trade', stock_info['Close'])
                logging.info(f"Based on daytrading pattern analysis, buying {stock_ticker}, Stock Score: {stock_score}")
        except Exception as e:
            logging.error(f"Error in daytrading_stock_analyzer: {e}")

def news_stock_analyzer(stock_ticker):
    try:
        stock_info = sdg.get_current_stock_data(stock_ticker)
        stock_score = 0
        stock_score += nc.sentiment_analyzer(news.get_news(stock_ticker))
        logging.info(f"{stock_ticker} news score: {stock_score}")
        if stock_score >= 0.35 and stock_ticker not in long_term_positions:
            alpaca.create_order(stock_ticker, 1)
            with position_lock:
                long_term_positions[stock_ticker] = stock_info['Close']
                active_positions_to_check[stock_ticker] = ('long_term', stock_info['Close'])
            logging.info(f"Based on News analysis, buying {stock_ticker}")
    except Exception as e:
        logging.error(f"News analysis not working for {stock_ticker}. Error: {e}")

def stock_position_analyzer():
    while True:
        with position_lock:
            for stock_ticker, (trade_type, purchase_price) in list(active_positions_to_check.items()):
                threading.Thread(target=check_perform_sell, args=(stock_ticker, trade_type, purchase_price)).start()
            active_positions_to_check.clear()
        time.sleep(const.ANALYSIS_INTERVAL)

def should_sell(current_price, purchase_price):
    return_price = (current_price - purchase_price) / purchase_price
    return 0.03 <= return_price <= 0.05

def check_perform_sell(stock_ticker, trade_type, purchase_price):
    while True:
        stock_info = sdg.get_current_stock_data(stock_ticker)  # Define stock_info here
        current_stock_price = stock_info['Close']
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
                        continue  # Move to the next iteration
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
                        continue  # Move to the next iteration
                logging.info(f"Sold {stock_ticker} from long term at {current_stock_price}")
                break
        time.sleep(const.ANALYSIS_INTERVAL)
class StrategyRunner:
    def __init__(self):
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

    def run_backtest(self, start_date, end_date, initial_balance):
        backtester = bt.Backtester(start_date, end_date, initial_balance)
        tickers = scraper.active_stocks() + const.STOCKS_TO_CHECK  # Pull the symbols from the scraper module and constants file
        batches = util.partition_array(tickers, 10)  # Split tickers into batches of 10
        strategy_metrics = {}
        for batch_num, batch in enumerate(batches):
            logging.info(f"Starting backtest for batch {batch_num + 1}/{len(batches)}: {batch}")
            for name, strategy in self.strategies.items():
                backtester.run_strategy(strategy, batch)
                final_balance = backtester.calculate_performance()
                logging.info(f"Final balance for {name} in batch {batch_num + 1}: {final_balance}")
                logging.info(f"Trades executed in batch {batch_num + 1}: {backtester.trades}")
                metrics = backtester.calculate_metrics()
                logging.info(f"Backtest metrics for {name} in batch {batch_num + 1}: {metrics}")
                strategy_metrics[name] = metrics
            logging.info(f"Completed backtest for batch {batch_num + 1}/{len(batches)}")
        logging.info("Completed backtest")
        return strategy_metrics

if __name__ == "__main__":
    logging.info("Starting the trading bot")

    # Initializing important stuff
    news = news.NewsGetter()
    alpaca = alp.Alpaca()
    day_trading_positions = {}  # key is stock ticker, value is stock purchase price
    long_term_positions = {}  # key is stock ticker, value is stock purchase price
    active_positions_to_check = {}

    positions = alpaca.get_positions()
    with position_lock:
        active_positions_to_check = {
            position.symbol: ('day_trade', float(position.cost_basis))
            for position in positions
        }
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
                logging.info("Market Close")

            # Execute the news analyzer for both constant stocks and active stocks from the scraper module
            for stock_ticker in const.STOCKS_TO_CHECK + scraper.active_stocks():
                threading.Thread(target=news_stock_analyzer, args=(stock_ticker,)).start()

            logging.info("Starting Backtester")
            threading.Thread(target=run_backtests).start()  # Run backtests after other tasks

            logging.info("Finished Backtester")
            time.sleep(3600)  # Wait for an hour before checking again
        except Exception as e:
            logging.error(f"Restarting due to error: {e}")
            time.sleep(60)  # Wait for a minute before retrying in case of an error