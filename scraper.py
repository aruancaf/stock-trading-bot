from bs4 import BeautifulSoup
import requests
import constants


urls = ["https://finance.yahoo.com/gainers", "https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks", "https://finance.yahoo.com/screener/predefined/day_gainers", "https://finance.yahoo.com/screener/predefined/growth_technology_stocks", "https://finance.yahoo.com/screener/predefined/most_actives", "https://finance.yahoo.com/screener/predefined/undervalued_large_caps", "https://finance.yahoo.com/screener/predefined/aggressive_small_caps", "https://finance.yahoo.com/screener/predefined/small_cap_gainers"]

def active_stocks():
    scraped_stocks = constants.STOCKS_TO_CHECK
    for url in urls:
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        results = soup.find(id="Lead-5-ScreenerResults-Proxy")
        assets = soup.get_text()
        for result in results.find_all('a'):
            href = result['href']
            if '=' in href: scraped_stocks.append(href[href.find('=') + 1:])
    return list(set(scraped_stocks))
