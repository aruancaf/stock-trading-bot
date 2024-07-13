import requests
from bs4 import BeautifulSoup
import logging
import pandas as pd
from typing import List, Dict

# List of URLs to scrape (Yahoo Finance screens) and corresponding CSV names
urls_and_csv_names = [
    ("https://finance.yahoo.com/screener/predefined/day_gainers", "Day_Gainers.csv"),
    ("https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks", "Undervalued_Growth_Stocks.csv"),
    ("https://finance.yahoo.com/screener/predefined/growth_technology_stocks", "Growth_Technology_Stocks.csv"),
    ("https://finance.yahoo.com/screener/predefined/most_actives", "Most_Actives.csv"),
    ("https://finance.yahoo.com/screener/predefined/undervalued_large_caps", "Undervalued_Large_Caps.csv"),
    ("https://finance.yahoo.com/screener/predefined/aggressive_small_caps", "Aggressive_Small_Caps.csv"),
    ("https://finance.yahoo.com/screener/predefined/small_cap_gainers", "Small_Cap_Gainers.csv")
]

# Configure logging to write to 'scraper.log' with level INFO
logging.basicConfig(filename='scraper.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to fetch active stocks from a given URL
def active_stocks(url: str) -> List[Dict[str, str]]:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url}, status code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'class': 'W(100%)'})
        if not table:
            logging.error(f"Failed to find the table in the page {url}")
            return []

        tickers = []
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            try:
                symbol = row.find('td', {'aria-label': 'Symbol'}).text.strip()
                name = row.find('td', {'aria-label': 'Name'}).text.strip()
                price = row.find('td', {'aria-label': 'Price (Intraday)'}).text.strip()
                change = row.find('td', {'aria-label': 'Change'}).text.strip()
                percent_change = row.find('td', {'aria-label': '% Change'}).text.strip()
                volume = row.find('td', {'aria-label': 'Volume'}).text.strip()
                tickers.append({
                    'Ticker': symbol,
                    'Name': name,
                    'Price': price,
                    'Change': change,
                    '% Change': percent_change,
                    'Volume': volume
                })
            except AttributeError as e:
                logging.error(f"Error parsing row: {e}")
                continue

        logging.info(f"Scraped tickers from {url}: {tickers}")
        return tickers

    except Exception as e:
        logging.error(f"Error in active_stocks for URL {url}: {e}")
        return []

# Function to scrape all URLs and return combined data
def scrape_all_urls() -> List[Dict[str, str]]:
    all_tickers = []
    for url, _ in urls_and_csv_names:
        tickers = active_stocks(url)
        all_tickers.extend(tickers)
    return all_tickers

if __name__ == "__main__":
    scraped_data = scrape_all_urls()
    print(scraped_data)