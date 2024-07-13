import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import credentials as cred

# Load environment variables from .env file
load_dotenv()

class Alpaca:
    def __init__(self):
        self.api = tradeapi.REST(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'), base_url='https://paper-api.alpaca.markets')
        self.account = self.api.get_account()
        self.api.list_positions()
        print("Account Status: ", self.account.status)

    def sell_position(self, ticker_symbol: str):
        self.api.close_position(ticker_symbol)
        print("Closed", ticker_symbol, "position")

    def sell_all_positions(self):
        self.api.close_all_positions()
        self.api.cancel_all_orders()
        print("Closed all positions")

    def get_positions_tickers(self):
        positions = self.api.list_positions()
        return [position.symbol for position in positions]

    def get_positions(self):
        return self.api.list_positions()

    def create_order(self, ticker_symbol: str, quantity: int):
        self.api.submit_order(symbol=ticker_symbol, qty=quantity, side='buy', type='market', time_in_force='day')
        print(quantity, ticker_symbol, "ordered")