import portfolio_manager
import trading_strategies
import yf_web_scraper
from utils import multithreading

while True:
    most_active_stocks = yf_web_scraper.get_active_tickers()
    portfolio_manager.get_adjusted_position_polarity()
    print(most_active_stocks)
    multithreading.run_thread(trading_strategies.evaluate_purchased_stocks)
    multithreading.run_chunked_threads(most_active_stocks, trading_strategies.run_stock_pipelines, 30)
