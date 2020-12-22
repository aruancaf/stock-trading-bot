import scraper
import threading
import time
from datetime import datetime
import stock_market_constants as const
import alpaca as alp

alpaca = alp.Alpaca()

time = datetime.now().strftime("%H:%M")
# time = "12:01"
while True:
    if time > const.STOCK_MARKET_OPEN_TIME and time < const.STOCK_MARKET_CLOSE_TIME:
        print("Market Open")
    else:
        print("Market Close")
        alpaca.sell_all_positions()
        time.sleep(3600)

# purchased_stocks_thread = threading.Thread(target=[Insert], args(1, )))
# stock_analysis_thread = threading.Thread(target=[Insert], args(1, )))

# purchased_stocks_thread.start()
# stock_analysis_thread.start()

