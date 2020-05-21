import requests
from bs4 import BeautifulSoup


def get_most_actives() -> []:
    active_stocks_p1 = []
    active_stocks_p2 = []
    headers = {
        'Referer': 'https://itunes.apple.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
    }

    page1 = requests.get("https://finance.yahoo.com/screener/predefined/most_actives?offset=0&count=100", headers)
    page2 = requests.get("https://finance.yahoo.com/screener/predefined/most_actives?count=100&offset=100", headers)
    soup1 = BeautifulSoup(page1.content, 'html.parser')
    soup2 = BeautifulSoup(page2.content, 'html.parser')

    for element in range(len(soup1.find_all('a'))):
        active_stocks_p1.append(soup1.find_all('a')[element].get_text())

    for element in range(len(soup2.find_all('a'))):
        active_stocks_p2.append(soup2.find_all('a')[element].get_text())

    lower_bound_p1 = active_stocks_p1.index("Heatmap View") + 1
    higher_bound_p1 = active_stocks_p1.index("Finance")

    lower_bound_p2 = active_stocks_p2.index("Heatmap View") + 1
    higher_bound_p2 = active_stocks_p2.index("Finance")

    return active_stocks_p1[lower_bound_p1:higher_bound_p1] + active_stocks_p2[lower_bound_p2:higher_bound_p2]
