import alpaca_trade_api as tradeapi
import credentials as cred

@Singleton
class Alpaca:
    def __init__(self):
        self.api = tradeapi.REST(cred.API_ID, cred.SECRET_KEY, base_url='https://paper-api.alpaca.markets')
        self.account  = api.get_account()
        self.api.list_positions()
        print("Account Status: ", account.status)

    def sell_all_positions(self):
        orders = self.alpaca.list_orders(status="open")
        for order in orders:
           self.alpaca.cancel_order(order.id)
        positions = self.alpaca.list_positions()
        for position in positions:
            self.alpaca.api.close_position(position)
    
    def get_positions(self):
        positions = self.alpaca.list_positions()
        positions_tickers[]
        for position in positions:
            positions_tickers += position.symbol
        return positions_tickers
