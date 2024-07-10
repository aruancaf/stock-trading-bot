import time
import logging
import re
from datetime import datetime, timedelta
from newsapi import NewsApiClient
import finnhub
import feedparser
import credentials as cred
import stock_data_gatherer as sdg
import util

class NewsGetter:
    def __init__(self):
        self.api = NewsApiClient(api_key=cred.NEWS_API_KEY)
        self.finnhub_client = finnhub.Client(api_key=cred.FINNHUB_API_KEY)
        self.newsapi_requests = 0
        self.finnhub_requests = 0
        self.last_newsapi_reset = datetime.now()
        self.last_finnhub_reset = datetime.now()
        self.rss_feeds = [
            "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",  # WSJ Markets
            "https://feeds.marketwatch.com/marketwatch/topstories/"  # MarketWatch Top Stories
        ]

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
            logging.warning(f"Reached NewsAPI limit for {stock}")
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

        return [
            news['description']
            for news in articles
            if util.check_overlap(search_terms, news['description'])
        ]

    def get_news_from_finnhub(self, stock):
        if self.finnhub_requests >= 70:
            logging.warning(f"Reached Finnhub limit for {stock}")
            return []

        company_name = re.sub(r'[^\w\s]', '', sdg.get_stock_company_name(stock))
        articles = self.finnhub_client.company_news(stock, _from="2022-01-01", to="2022-12-31")

        self.finnhub_requests += 1

        return [
            news['summary']
            for news in articles
            if util.check_overlap(company_name, news['summary'])
        ]

    def fetch_rss_feed(self, url):
        try:
            return feedparser.parse(url)
        except Exception as e:
            logging.error(f"Error fetching RSS feed {url}: {e}")
            return None

    def parse_feed(self, feed):
        articles = []
        if 'entries' in feed:
            for entry in feed['entries']:
                article = {
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', 'No Link'),
                    'summary': entry.get('summary', 'No Summary')
                }
                articles.append(article)
        return articles

    def fetch_and_parse_all_feeds(self):
        all_articles = []
        for url in self.rss_feeds:
            if feed := self.fetch_rss_feed(url):
                articles = self.parse_feed(feed)
                all_articles.extend(articles)
            time.sleep(1)  # Add sleep to respect rate limits
        return all_articles

    def get_news(self, stock):
        self.reset_request_counts()
        newsapi_news = self.get_news_from_newsapi(stock)
        finnhub_news = self.get_news_from_finnhub(stock)
        rss_news = self.fetch_and_parse_all_feeds()
        return newsapi_news + finnhub_news + [article['summary'] for article in rss_news]
