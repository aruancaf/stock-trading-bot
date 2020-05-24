import trading_strategies
import yf_web_scraper
from utils import multithreading
import portfolio_manager

while True:
    most_active_stocks = yf_web_scraper.get_active_tickers()
    portfolio_manager.get_position_polarity()
    multithreading.run_chunked_threads(most_active_stocks, trading_strategies.run_stock_pipelines, 35)
