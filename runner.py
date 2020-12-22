import scraper
import threading
import time
from datetime import datetime
import stock_market_constants as const
import alpaca as alp
import stock_analysis as sa

alpaca = alp.Alpaca()

time = datetime.now().strftime("%H:%M")
# time = "12:01"
while True:
    if time > const.STOCK_MARKET_OPEN_TIME and time < const.STOCK_MARKET_CLOSE_TIME:
        print("Market Open")
        stock_analyzer()
        stock_position_analyzer()
    else:
        print("Market Close")
        alpaca.sell_all_positions()
        time.sleep(3600)

# purchased_stocks_thread = threading.Thread(target=[Insert], args(1, )))
# stock_analysis_thread = threading.Thread(target=[Insert], args(1, )))

# purchased_stocks_thread.start()
# stock_analysis_thread.start()

def stock_analyzer():
    active_stocks = scraper.active_stocks()
    stock_score = 0
    for stock_ticker in active_stocks:
        stock_score += sa.moving_average_checker(stock_ticker)
        if stock_score > 0.7:
            alpaca.create_order(stock_ticker, 1)

def stock_position_analyzer():
    positions = alpaca.get_positions()
    for position in positions:
        if sa.moving_average_checker(position) < 0:
            alpaca.sell_position(position)
