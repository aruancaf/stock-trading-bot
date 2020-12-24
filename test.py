import news_classifier
import news
import stock_data_gatherer as sdg
import constants

b = news.NewsGetter()

for ticker in constants.STOCKS_TO_CHECK:
    print("Ticker Symbol", ticker, "Stock score:", news_classifier.sentiment_analyzer(b.get_news(ticker)))
