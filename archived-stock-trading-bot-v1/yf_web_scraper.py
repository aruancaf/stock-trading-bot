import requests
from bs4 import BeautifulSoup

# todo
# url = "https://finance.yahoo.com/gainers"
# soup = BeautifulSoup(requests.get(url).text, 'html.parser')
# assets = soup.find_all('a', attrs={"class": "Fw(600)"})

headers = {
    'Referer': 'https://itunes.apple.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
}


def get_active_tickers() -> []:
    return scrape_trending_tickers() + scrape_screeners()


def scrape_screeners() -> []:
    active_stocks = []

    yf_screener_urls = ["https://finance.yahoo.com/screener/predefined/most_actives?offset=0&count=100",
                        "https://finance.yahoo.com/screener/predefined/most_actives?count=100&offset=100",
                        "https://finance.yahoo.com/screener/predefined/day_gainers",
                        "https://finance.yahoo.com/screener/predefined/small_cap_gainers",
                        "https://finance.yahoo.com/screener/predefined/aggressive_small_caps?offset=0&count=100",
                        "https://finance.yahoo.com/screener/predefined/day_losers?offset=0&count=100"]

    for url in yf_screener_urls:
        soup = BeautifulSoup(requests.get(url, headers).content, 'html.parser')
        screener_list = []
        for element in soup.find_all('a'):
            screener_list.append(element.get_text())
        try:
            active_stocks += screener_list[screener_list.index("Heatmap View") + 1: screener_list.index("Finance")]
        except ValueError:
            scrape_screeners()
    return active_stocks


def scrape_trending_tickers() -> []:
    yf_trending_ticker_urls = ["https://finance.yahoo.com/trending-tickers"]

    active_stocks = []
    for url in yf_trending_ticker_urls:
        soup = BeautifulSoup(requests.get(url, headers).content, 'html.parser')
        soup_list = list(soup.find_all('td'))
        for element in range(0, len(soup_list)):
            if element % 12 == 0:
                active_stocks.append(soup_list[element].get_text())

    return active_stocks
