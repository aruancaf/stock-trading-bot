import trading_strategies
import yf_web_scraper

while True:
    most_active_stocks = yf_web_scraper.get_most_actives()
    trading_strategies.trend_following(most_active_stocks)
