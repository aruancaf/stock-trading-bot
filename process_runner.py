import portfolio_manager
import trading_strategies
import yf_web_scraper
from utils import multithreading, json_simplifier as json_simp

json_simp.read_json()
most_active_stocks = yf_web_scraper.get_active_tickers()
print(most_active_stocks)
portfolio_manager.print_adjusted_position_polarity()
multithreading.run_thread(trading_strategies.evaluate_purchased_stocks)
while True:
    json_simp.read_json()
    most_active_stocks = yf_web_scraper.get_active_tickers()
    multithreading.run_chunked_threads(most_active_stocks, trading_strategies.run_stock_pipelines, 32)
