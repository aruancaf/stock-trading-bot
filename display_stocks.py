import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import news_classifier
import news
import stock_data_gatherer as sdg
import constants

# Create a NewsGetter instance
b = news.NewsGetter()

# Function to plot sentiment scores over time
def plot_sentiment(ticker, days=30):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = []
    scores = []
    for single_date in pd.date_range(start=start_date, end=end_date):
        news_articles = b.get_news(ticker, date=single_date.strftime("%Y-%m-%d"))
        score = news_classifier.sentiment_analyzer(news_articles)
        dates.append(single_date)
        scores.append(score)
    
    plt.figure(figsize=(10, 5))
    plt.plot(dates, scores, label=ticker)
    plt.xlabel('Date')
    plt.ylabel('Sentiment Score')
    plt.title(f'Sentiment Score Over Time for {ticker}')
    plt.legend()
    plt.show()

# Function to plot volume data
def plot_volume(ticker, n=180):
    stock_prices = [
        sdg.get_historical_data(ticker, "1d", "1m").iloc[i].to_dict()['Volume']
        for i in range(-n, 0)
    ]
    plt.plot(list(range(n)), stock_prices, 'xb-')
    plt.xlabel('Time')
    plt.ylabel('Volume')
    plt.title(f'Volume Over Time for {ticker}')
    plt.show()

    print(f"Price Slope for {ticker}: ", sdg.get_volume_slope(ticker)/(0.2*sdg.get_current_stock_data(ticker)['Volume']))

# Plot sentiment and volume for each ticker
for ticker in constants.STOCKS_TO_CHECK:
    plot_volume(ticker)
    plot_sentiment(ticker)