import logging
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import news_classifier
import news
import stock_data_gatherer as sdg
import constants

# Configure logging to write to a file
logging.basicConfig(filename='sentiment_scores.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

# Create a database connection and a table for storing sentiment scores
conn = sqlite3.connect('sentiment_scores.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS sentiment_scores
             (ticker text, score real, date text)''')

# Create a NewsGetter instance
b = news.NewsGetter()

# Function to compute and analyze average sentiment scores over time
def get_historical_sentiment(ticker, days=30):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    scores = []
    for single_date in pd.date_range(start=start_date, end=end_date):
        news_articles = b.get_news(ticker, date=single_date.strftime("%Y-%m-%d"))
        score = news_classifier.sentiment_analyzer(news_articles)
        scores.append(score)
    return sum(scores) / len(scores)

# Process each ticker symbol
for ticker in constants.STOCKS_TO_CHECK:
    score = news_classifier.sentiment_analyzer(b.get_news(ticker))
    log_message = f"Ticker Symbol: {ticker}, Stock score: {score}"
    print(log_message)
    logging.info(log_message)
    c.execute("INSERT INTO sentiment_scores VALUES (?, ?, ?)", 
              (ticker, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

    # Compute historical sentiment
    average_score = get_historical_sentiment(ticker)
    historical_log_message = f"Ticker Symbol: {ticker}, Average Stock score over 30 days: {average_score}"
    print(historical_log_message)
    logging.info(historical_log_message)

# Close the database connection
conn.close()