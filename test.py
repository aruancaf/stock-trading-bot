import news_classifier
import news
import stock_data_gatherer as sdg

ticker = "AAPL"

b = news.NewsGetter()

a = b.get_news(ticker + " " + sdg.get_stock_company_name(ticker))

for i in a:
    print(i)
    news_classifier.sentiment_analyzer(i)
    print("\n\n\n\n")

