import requests
from bs4 import BeautifulSoup


def get_most_actives() -> []:
    active_stocks = []
    headers = {
        'Referer': 'https://itunes.apple.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
    }
    urls = ["https://finance.yahoo.com/trending-tickers"]
    # "https://finance.yahoo.com/screener/predefined/most_actives?offset=0&count=100",
    # "https://finance.yahoo.com/screener/predefined/most_actives?count=100&offset=100"]

    active_stocks = []
    for url in urls:
        soup = BeautifulSoup(requests.get(url, headers).content, 'html.parser')
        soupList = list(soup.find_all('td'))
        for element in range(0, len(soupList)):
            if element % 12 == 0:
                active_stocks.append(soupList[element].get_text())

    # active_stocks += temp_list[temp_list.index("Heatmap View") + 1: temp_list.index("Finance")]

    return active_stocks
    # return active_stocks_p1[lower_bound_p1:higher_bound_p1] + active_stocks_p2[lower_bound_p2:higher_bound_p2]
