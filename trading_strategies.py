import math
import time
from datetime import datetime

import yfinance as yf

import portfolio_manager
import trading_constants
import yf_extender

first_run = True


def run_stock_pipelines(stock_database: [str]):
    for ticker_symbol in stock_database:
        if ticker_symbol not in trading_constants.blacklist:
            try:
                trend_following_polarity = trend_following(ticker_symbol)
                ema_crossover_polarity = ema_crossover(ticker_symbol)
                console_output = "{0} price: {1} at {2}, strategy polarity: {3}\n".format(ticker_symbol,
                                                                                          (yf_extender.get_stock_state(
                                                                                              yf.Ticker(ticker_symbol))[
                                                                                               'Close'] * 1000) / 1000,
                                                                                          datetime.now().strftime(
                                                                                              "%H:%M:%S"),
                                                                                          trend_following_polarity + ema_crossover_polarity)
                print(console_output, end='')
                if (trend_following_polarity + ema_crossover_polarity) >= 0.5:
                    stock_price = yf_extender.get_stock_state(yf.Ticker(ticker_symbol))['Close']
                    stock_quantity = math.floor(
                        portfolio_manager.buying_power * trading_constants.max_investment_partition * (
                                trend_following_polarity + ema_crossover_polarity) /
                        stock_price)
                    if stock_quantity > 0 and portfolio_manager.buying_power > (stock_quantity * stock_price):
                        portfolio_manager.buy_stock(ticker_symbol, stock_quantity)

            except IndexError:
                print(ticker_symbol + ": No Data")


def trend_following(ticker_symbol: str):
    ticker = yf.Ticker(ticker_symbol)
    stock_info = yf_extender.get_stock_state(ticker)
    previous_2mo_high = yf_extender.previous_high(ticker, "2mo")
    if previous_2mo_high < stock_info['Close'] and yf_extender.get_high2current_price_change_percent(
            ticker) > -0.0025:
        return 0.2
    return 0.0


def ema_crossover(ticker_symbol: str):
    ticker = yf.Ticker(ticker_symbol)
    stock_info = yf_extender.get_stock_state(ticker)
    stock_history = ticker.history(period="1d", interval="5m")
    previous_price = stock_history.iloc[len(stock_history) - 2].to_dict()['Close']
    ticker_ema = yf_extender.calculate_ema(ticker)
    ticker_previous_ema = yf_extender.calculate_previous_ema(ticker)

    if stock_info['Close'] > ticker_ema and previous_price < ticker_previous_ema and stock_info['Close'] > 3:
        print(
            ticker_symbol + " previous price ema {0} previous price {1} current price ema {2} current price {3} direction {4}".format(
                ticker_previous_ema, previous_price, ticker_ema, stock_info['Close'],
                yf_extender.get_direction(ticker)))

        return 0.5
    return 0.0


def evaluate_purchased_stocks():
    time.sleep(2)
    while True:
        purchased_copy = dict(portfolio_manager.purchased)
        for ticker_symbol in purchased_copy:
            ticker = yf.Ticker(ticker_symbol)
            stock_info = yf_extender.get_stock_state(ticker)
            price_change_since_purchase = stock_info['Close'] - purchased_copy[ticker_symbol]['Close']
            print("Checking " + ticker_symbol + " | Direction: {0} | Price Change: {1} | Gains/Losses: {2}".format(
                yf_extender.get_direction(ticker), price_change_since_purchase,
                price_change_since_purchase * purchased_copy[ticker_symbol]['Quantity']))
            if stock_info['Close'] < yf_extender.calculate_ema(ticker):
                print("Because stock price dropped below EMA line, " + ticker_symbol)
                portfolio_manager.sell_stock(ticker_symbol)
                break
            elif yf_extender.get_direction(ticker) < -0.001: #should depend on proportion
                print("Because direction is downward {0}".format(
                    yf_extender.get_direction(ticker)))
                portfolio_manager.sell_stock(ticker_symbol)
                break
            time.sleep(0.1)
