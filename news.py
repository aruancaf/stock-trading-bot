from newsapi import NewsApiClient
import finnhub
import credentials as cred
import stock_data_gatherer as sdg
import re
import util
import scraper
from datetime import datetime, timedelta
import time

class NewsGetter:
    def __init__(self):
        self.api = NewsApiClient(api_key=cred.NEWS_API_KEY)
        self.finnhub_client = finnhub.Client(api_key=cred.FINNHUB_API_KEY)
        self.newsapi_requests = 0
        self.finnhub_requests = 0
        self.last_newsapi_reset = datetime.now()
        self.last_finnhub_reset = datetime.now()

    def reset_request_counts(self):
        current_time = datetime.now()
        if current_time - self.last_newsapi_reset > timedelta(hours=12):
            self.newsapi_requests = 0
            self.last_newsapi_reset = current_time
        if current_time - self.last_finnhub_reset > timedelta(hours=12):
            self.finnhub_requests = 0
            self.last_finnhub_reset = current_time

    def get_news_from_newsapi(self, stock):
        if self.newsapi_requests >= 50:
            print(f"Reached NewsAPI limit for {stock}")
            return []

        company_name = re.sub(r'[^\w\s]', '', sdg.get_stock_company_name(stock))
        search_terms = f"{stock} {company_name}"
        articles = self.api.get_everything(
            q=stock,
            qintitle=f"{stock} OR {company_name}",
            language='en',
            page_size=100
        )['articles']

        self.newsapi_requests += 1

        news_descriptions = []
        for news in articles:
            if util.check_overlap(search_terms, news['description']):
                news_descriptions.append(news['description'])
        return news_descriptions

    def get_news_from_finnhub(self, stock):
        if self.finnhub_requests >= 50:
            print(f"Reached Finnhub limit for {stock}")
            return []

        company_name = re.sub(r'[^\w\s]', '', sdg.get_stock_company_name(stock))
        articles = self.finnhub_client.company_news(stock, _from="2022-01-01", to="2022-12-31")

        self.finnhub_requests += 1

        news_descriptions = []
        for news in articles:
            if util.check_overlap(company_name, news['summary']):
                news_descriptions.append(news['summary'])
        return news_descriptions

    def get_news(self, stock):
        current_hour = datetime.now().hour
        if 18 <= current_hour or current_hour < 3:
            # Limit requests between 6 PM and 3 AM
            time.sleep(3600)  # Sleep for an hour
            return self.get_news_from_newsapi(stock) + self.get_news_from_finnhub(stock)
        else:
            self.reset_request_counts()
            newsapi_news = self.get_news_from_newsapi(stock)
            finnhub_news = self.get_news_from_finnhub(stock)
            return newsapi_news + finnhub_news


 