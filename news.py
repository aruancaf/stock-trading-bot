from newsapi import NewsApiClient
import credentials as cred
import pprint



class NewsGetter:
    def __init__(self):
        self.api = NewsApiClient(api_key=cred.NEWS_API_KEY)

    def get_news(self, stock):
        articles = self.api.get_everything(q=stock, language='en', sort_by='relevancy')['articles']
        news_descriptions = []
        for news in articles:
            news_descriptions.append(news['description'])
        return news_descriptions
