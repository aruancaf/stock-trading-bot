from bs4 import BeautifulSoup
import requests
import constants
import logging


urls = ["https://finance.yahoo.com/gainers", "https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks", "https://finance.yahoo.com/screener/predefined/day_gainers", "https://finance.yahoo.com/screener/predefined/growth_technology_stocks", "https://finance.yahoo.com/screener/predefined/most_actives", "https://finance.yahoo.com/screener/predefined/undervalued_large_caps", "https://finance.yahoo.com/screener/predefined/aggressive_small_caps", "https://finance.yahoo.com/screener/predefined/small_cap_gainers"]
# Configure logging
logging.basicConfig(filename='scraper.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def active_stocks():
    try:
        response = requests.get('https://www.example.com/active-stocks')
        if response.status_code != 200:
            logging.error(f"Failed to fetch data, status code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.find('div', {'class': 'results'})
        if not results:
            logging.error("Failed to find the 'results' div in the page")
            return []

        tickers = []
        for result in results.find_all('a'):
            tickers.append(result.text.strip())
        
        logging.info(f"Scraped tickers: {tickers}")
        return tickers

    except Exception as e:
        logging.error(f"Error in active_stocks: {e}")
        return []