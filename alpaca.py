import alpaca_trade_api as tradeapi
import credentials as cred

api = tradeapi.REST(cred.API_ID, cred.SECRET_KEY, base_url='https://paper-api.alpaca.markets')
account  = api.get_account()
api.list_positions()

print(account.status)

api.polygon.news('AAPL')
