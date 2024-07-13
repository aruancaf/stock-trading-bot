from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY')
NEW_RELIC_LICENSE_KEY = os.getenv("NEW_RELIC_LICENSE_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets/v2")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
QUANDL_API_KEY = os.getenv("QUANDL_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")
DATABASE_URL = os.getenv("DATABASE_URL")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
MORNINGSTAR_API_KEY = os.getenv("MORNINGSTAR_API_KEY")
# Debugging: print environment variables to ensure they are loaded
print(f"ALPACA_API_KEY: {ALPACA_API_KEY}")
print(f"ALPACA_SECRET_KEY: {ALPACA_SECRET_KEY}")