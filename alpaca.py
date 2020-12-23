import alpaca_trade_api as tradeapi
import credentials as cred
# import runner

class Alpaca:
    def __init__(self):
        self.api = tradeapi.REST(cred.ALP_API_ID, cred.ALP_SECRET_KEY, base_url='https://paper-api.alpaca.markets')
        self.account  = self.api.get_account()
        self.api.list_positions()
        print("Account Status: ", self.account.status)

    def sell_position(self, ticker_symbol: str):
        self.api.close_position(ticker_symbol)
        print("Closed", ticker_symbol, "position")

    def sell_all_positions(self):
        orders = self.api.list_orders(status="open")
        for order in orders:
            self.api.cancel_order(order.id)
        positions = self.api.list_positions()
        for position in positions:
            self.api.close_position(position.symbol)
        print("Closed all positions")

    def get_positions_tickers(self):
        positions = self.api.list_positions()
        positions_tickers = []
        for position in positions:
            positions_tickers.append(position.symbol)
        return positions_tickers

    def get_positions(self):
        positions = self.api.list_positions()
        return positions

    def create_order(self, ticker_symbol: str, quantity: int):
        self.api.submit_order(symbol=ticker_symbol, qty=quantity, side='buy', type='market', time_in_force='day')
        print(quantity, ticker_symbol, "ordered")
        # runner.active_positions_to_check[ticker_symbol] = 
