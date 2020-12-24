import news_classifier
import news
import stock_data_gatherer as sdg

ticker = "AAPL"

b = news.NewsGetter()

a = b.get_news(ticker)

print("Stock score:", news_classifier.sentiment_analyzer(a))
