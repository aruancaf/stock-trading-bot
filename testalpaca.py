import alpaca
import time

alp = alpaca.Alpaca()
alp.create_order('TSLA', 1)
time.sleep(10)
alp.sell_all_positions()
