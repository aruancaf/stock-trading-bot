import alpaca_trade_api as tradeapi
import credentials as cred

@Singleton
class Alpaca:
    def __init__(self):
        self.api = tradeapi.REST(cred.API_ID, cred.SECRET_KEY, base_url='https://paper-api.alpaca.markets')
        self.account  = api.get_account()
        self.api.list_positions()
        print("Account Status: ", account.status)

    def sell_position(self, ticker_symbol: str):
        positions = self.api.list_positions()
        position_sell = None
        for position in positions:
            if position.symbol == ticker_symbol:
                position_sell = position
                self.api.close_position(position_sell)
                return

    def sell_all_positions(self):
        orders = self.api.list_orders(status="open")
        for order in orders:
           self.api.cancel_order(order.id)
        positions = self.api.list_positions()
        for position in positions:
            self.api.close_position(position)
    
    def get_positions(self):
        positions = self.api.list_positions()
        positions_tickers[]
        for position in positions:
            positions_tickers += position.symbol
        return positions_tickers

    def create_order(self, ticker_symbol: str, quantity: int):
        api.submit_order(symbol=ticker_symbol, qty=quantity, side='buy', type='market', time_in_force='day')
