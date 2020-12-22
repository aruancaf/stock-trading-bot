import stock_analysis
import scraper
import stock_data_gatherer

for stock_ticker in scraper.active_stocks():
    print(stock_data_gatherer.get_current_stock_data(stock_ticker))
    print(stock_ticker,": ",stock_analysis.moving_average_checker(stock_ticker))

