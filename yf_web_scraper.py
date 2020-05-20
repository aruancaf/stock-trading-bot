import requests
from bs4 import BeautifulSoup


def get_most_actives() -> []:
    active_stocks = []
    page = requests.get("https://finance.yahoo.com/screener/predefined/most_actives?offset=0&count=100")
    soup = BeautifulSoup(page.content, 'html.parser')

    for x in range(len(soup.find_all('a'))):
        active_stocks.append(soup.find_all('a')[x].get_text())

    lower_bound = active_stocks.index("Heatmap View")
    higher_bound = active_stocks.index("Finance") - 1
    for x in range(len(active_stocks) - 1, -1, -1):
        if x <= lower_bound or x > higher_bound:
            active_stocks.pop(x)

    return active_stocks

