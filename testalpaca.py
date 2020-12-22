import alpaca
import time

alp = alpaca.Alpaca()
alp.create_order('TSLA', 10)
alp.create_order('AAPL', 10)
