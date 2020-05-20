import requests
from bs4 import BeautifulSoup


def get_most_actives() -> []:
    active_stocks = []
    page = requests.get("https://finance.yahoo.com/screener/predefined/most_actives?offset=0&count=230")
    soup = BeautifulSoup(page.content, 'html.parser')

    for x in range(len(soup.find_all('a'))):
        active_stocks.append(soup.find_all('a')[x].get_text())

    lower_bound = active_stocks.index("Heatmap View") + 1
    higher_bound = active_stocks.index("Finance")

    return active_stocks[lower_bound:higher_bound]
