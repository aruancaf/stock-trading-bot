import math
import time
from datetime import datetime

import yfinance as yf

import portfolio_manager
import trading_constants
import yf_extender


def run_stock_pipelines(stock_database: [str]):
    for ticker_symbol in stock_database:
        if ticker_symbol not in trading_constants.blacklist:
            try:
                trend_following_confidence = trend_following(ticker_symbol)
                ema_crossover_confidence = ema_crossover(ticker_symbol)
                console_output = "{0} price: {1} at {2} \n".format(ticker_symbol,
                                                                   (yf_extender.get_stock_state(
                                                                       yf.Ticker(ticker_symbol))['Close'] * 1000)/1000,
                                                                   datetime.now().strftime("%H:%M:%S"))
                print(console_output, end='')
                if trend_following_confidence and ema_crossover_confidence is not None and trend_following_confidence + ema_crossover_confidence >= 0.5:
                    stock_quantity = math.floor(
                        portfolio_manager.buying_power * trading_constants.max_investment_partition * (
                                trend_following_confidence + ema_crossover_confidence) /
                        yf_extender.get_stock_state(yf.Ticker(ticker_symbol))['Close'])
                    if stock_quantity > 0:
                        portfolio_manager.buy_stock(yf.Ticker(ticker_symbol), stock_quantity)

            except IndexError:
                print("No data")


def trend_following(ticker_symbol: str):
    try:
        ticker = yf.Ticker(ticker_symbol)
        stock_info = yf_extender.get_stock_state(ticker)
        previous_2mo_high = yf_extender.previous_high(ticker, "2mo")
        if previous_2mo_high < stock_info['Close'] and yf_extender.get_high2current_price_change_percent(
                ticker) > -0.0025:
            return 0.5
        return 0
    except IndexError:
        print("No Data")
        return None


def ema_crossover(ticker_symbol: str):
    try:
        ticker = yf.Ticker(ticker_symbol)
        stock_info = yf_extender.get_stock_state(ticker)
        stock_history = ticker.history("5d")
        ticker_ema = yf_extender.calculate_ema(ticker)
        ticker_yesterday_ema = yf_extender.calculate_yesterday_ema(ticker)

        if stock_info['Close'] - ticker_ema > trading_constants.ema_cross_threshold and \
                stock_history.iloc[len(stock_history) - 2].to_dict()['Close'] < ticker_yesterday_ema and stock_info[
            'Close'] > ticker_ema:
            # print("{0} ema: {1} yesterday_ema: {2} current_price {3}".format(ticker_symbol, ticker_ema,
            #                                                                  ticker_yesterday_ema, stock_info['Close']))
            return 0.5
        return 0
    except IndexError:
        return None


def evaluate_purchased_stocks():
    time.sleep(5)
    while True:
        for ticker_symbol in dict(portfolio_manager.purchased):
            ticker = yf.Ticker(ticker_symbol)
            stock_info = yf_extender.get_stock_state(ticker)
            if stock_info['Close'] < yf_extender.calculate_ema(
                    ticker):
                print("Because stock price dropped below EMA line, ")
                time.sleep(0.2)
                portfolio_manager.sell_stock(ticker)
                break
            elif yf_extender.get_high2current_price_change_percent(ticker) < -0.0035:
                print("Because high 2 current price change is large {0}".format(
                    yf_extender.get_high2current_price_change_percent(ticker)))
                time.sleep(0.2)
                portfolio_manager.sell_stock(ticker)
                break
            time.sleep(0.3)
