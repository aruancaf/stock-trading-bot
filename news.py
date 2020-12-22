from newsapi import NewsApiClient
import credentials as cred
import pprint

api = NewsApiClient(api_key=cred.NEWS_API_KEY)

articles = api.get_everything(q='AAPL', language='en', sort_by='relevancy')['articles']

for news in articles:
    print(news, "\n")
