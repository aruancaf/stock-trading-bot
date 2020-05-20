import requests
from bs4 import BeautifulSoup


def get_most_actives() -> []:
    active_stocks = []
    headers = {
        'Referer': 'https://itunes.apple.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
    }

    page = requests.get("https://finance.yahoo.com/screener/predefined/most_actives?offset=0&count=150", headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    for x in range(len(soup.find_all('a'))):
        active_stocks.append(soup.find_all('a')[x].get_text())

    lower_bound = active_stocks.index("Heatmap View") + 1
    higher_bound = active_stocks.index("Finance")

    return active_stocks[lower_bound:higher_bound]
