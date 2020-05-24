import sys
import time
from datetime import datetime

import yfinance as yf

import portfolio_manager
import trading_constants
import yf_extender


def run_stock_pipelines(stock_database: [str]):
    for ticker_symbol in stock_database:
        trend_following_confidence = trend_following(ticker_symbol)
        ema_crossover_confidence = ema_crossover(ticker_symbol)
        if trend_following_confidence and ema_crossover_confidence is not None:
            sys.stdout.flush()
            print("{0} price: {1} at {2}".format(ticker_symbol,
                                                 yf_extender.get_stock_info(yf.Ticker(ticker_symbol))['Close'],
                                                 datetime.now().strftime("%H:%M:%S")))


def trend_following(ticker_symbol: str):
    try:
        ticker = yf.Ticker(ticker_symbol)
        stock_info = yf_extender.get_stock_info(ticker)
        previous_2mo_high = yf_extender.previous_high(ticker, "2mo")
        if previous_2mo_high < stock_info['Close'] and (stock_info['High'] - stock_info['Close']) < 0.05:
            portfolio_manager.buy_stock(ticker)
        time.sleep(0.1)
        return 0.5
    except IndexError:
        print("No Data")
        return None


def ema_crossover(ticker_symbol: str):
    try:
        ticker = yf.Ticker(ticker_symbol)
        stock_info = yf_extender.get_stock_info(ticker)
        ticker_ema = yf_extender.calculate_ema(ticker)
        print("{0} ema: {1}".format(ticker_symbol, ticker_ema))
        if stock_info['Close'] - ticker_ema > trading_constants.ema_cross_threshold:
            portfolio_manager.buy_stock(ticker)
        time.sleep(0.1)
        return 0.5
    except IndexError:
        return None

# def evaluate_purchased_stocks():
#     for ticker in portfolio_manager.stocks:
