import yfinance as yf
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nytimesarticle import articleAPI
from datetime import datetime, timedelta


date = datetime.today() - timedelta(days=5)
date = date.strftime('%Y%m%d')

print(date)


# newsAnalyzer = SentimentIntensityAnalyzer()
api = articleAPI("rpGF0Ig2GV85kKfg")

tickerSymbol = yf.Ticker("AAPL")

print(tickerSymbol.get_info()['symbol'])

#
stockNewsArticles = api.search(q=tickerSymbol.get_info()['symbol'],
     begin_date=date)

print(stockNewsArticles)
#
# get stock info
# print(tickerSymbol.history("1d").iloc[0])
# print(tickerSymbol.quarterly_financials())
