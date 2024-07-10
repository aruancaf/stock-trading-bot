import requests
from bs4 import BeautifulSoup
from typing import List

headers = {
    'Referer': 'https://itunes.apple.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
}

def get_active_tickers() -> List[str]:
    return scrape_trending_tickers() + scrape_screeners()

def scrape_screeners() -> List[str]:
    active_stocks = []

    yf_screener_urls = [
        "https://finance.yahoo.com/screener/predefined/most_actives?offset=0&count=100",
        "https://finance.yahoo.com/screener/predefined/most_actives?count=100&offset=100",
        "https://finance.yahoo.com/screener/predefined/day_gainers",
        "https://finance.yahoo.com/screener/predefined/small_cap_gainers",
        "https://finance.yahoo.com/screener/predefined/aggressive_small_caps?offset=0&count=100",
        "https://finance.yahoo.com/screener/predefined/day_losers?offset=0&count=100"
    ]

    for url in yf_screener_urls:
        soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')
        active_stocks.extend(
            element.get_text()
            for element in soup.find_all('a', attrs={"data-test": "quoteLink"})
        )
    return active_stocks

def scrape_trending_tickers() -> List[str]:
    yf_trending_ticker_urls = ["https://finance.yahoo.com/trending-tickers"]

    active_stocks = []
    for url in yf_trending_ticker_urls:
        soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')
        soup_list = list(soup.find_all('td'))
        active_stocks.extend(
            soup_list[element].get_text()
            for element in range(len(soup_list))
            if element % 12 == 0
        )
    return active_stocks