import requests
from bs4 import BeautifulSoup


headers = {
        'Referer': 'https://itunes.apple.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
    }

def get_most_actives() -> []:
   return scrape_top_tickers() + scrape_screeners()

def scrape_screeners():
    active_stocks = []

    urls = ["https://finance.yahoo.com/screener/predefined/most_actives?offset=0&count=100",
            "https://finance.yahoo.com/screener/predefined/most_actives?count=100&offset=100",
            "https://finance.yahoo.com/screener/predefined/day_gainers",
            "https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks",
            "https://finance.yahoo.com/screener/predefined/small_cap_gainers"]

    for url in urls:
        soup = BeautifulSoup(requests.get(url, headers).content, 'html.parser')
        temp_list = []
        for element in soup.find_all('a'):
            temp_list.append(element.get_text())
        active_stocks += temp_list[temp_list.index("Heatmap View") + 1: temp_list.index("Finance")]

    return active_stocks

def scrape_top_tickers():

    urls = ["https://finance.yahoo.com/trending-tickers"]

    active_stocks = []
    for url in urls:
        soup = BeautifulSoup(requests.get(url, headers).content, 'html.parser')
        soupList = list(soup.find_all('td'))
        for element in range(0, len(soupList)):
            if element % 12 == 0:
                active_stocks.append(soupList[element].get_text())

    return active_stocks
