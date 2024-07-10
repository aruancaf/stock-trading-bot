import math
import time
from datetime import datetime
import yfinance as yf
import portfolio_manager
import trading_constants
import yf_extender
from typing import List
import logging

first_run = True

def get_stock_state(ticker_symbol: str):
    ticker = yf.Ticker(ticker_symbol)
    history = ticker.history(period="1d")
    
    if history.empty:
        logging.warning(f"No data available for ticker {ticker_symbol}")
        return None

    stock_info = history.iloc[0].to_dict()
    stock_info['Time'] = datetime.now().strftime("%H:%M:%S")
    stock_info.pop('Dividends', None)
    stock_info.pop('Stock Splits', None)
    
    return stock_info

def trend_following(ticker_symbol: str):
    stock_info = get_stock_state(ticker_symbol)
    
    if stock_info is None:
        return 0  # Or handle the case where stock_info is None in another appropriate way

    previous_2mo_high = yf_extender.previous_high(ticker_symbol, "2mo")
    
    if previous_2mo_high is None or stock_info['Close'] is None:
        logging.warning(f"Previous high or current close price is None for ticker {ticker_symbol}")
        return 0
    
    if previous_2mo_high < stock_info['Close'] and yf_extender.get_high2current_price_change_percent(ticker_symbol) > -0.0025:
        return 0.2
    
    return 0.0

def run_stock_pipelines(stock_database: List[str]):
    for ticker_symbol in stock_database:
        if ticker_symbol not in trading_constants.blacklist:
            try:
                trend_following_polarity = trend_following(ticker_symbol)
                ema_crossover_polarity = ema_crossover(ticker_symbol)
                trix_polarity = trix_strategy(ticker_symbol)
                aroon_polarity = aroon_strategy(ticker_symbol)
                elder_ray_polarity = elder_ray_strategy(ticker_symbol)

                combined_polarity = (trend_following_polarity + ema_crossover_polarity +
                                     trix_polarity + aroon_polarity + elder_ray_polarity)

                stock_info = get_stock_state(ticker_symbol)
                if stock_info is None:
                    continue

                console_output = f"{ticker_symbol} price: {(stock_info['Close'] * 1000) / 1000} at {datetime.now().strftime('%H:%M:%S')}, strategy polarity: {combined_polarity}\n"
                print(console_output, end='')

                if combined_polarity >= 0.5:
                    stock_price = stock_info['Close']
                    stock_quantity = math.floor(
                        portfolio_manager.buying_power * trading_constants.max_investment_partition *
                        combined_polarity / stock_price)

                    if stock_quantity > 0 and portfolio_manager.buying_power > (stock_quantity * stock_price):
                        portfolio_manager.buy_stock(ticker_symbol, stock_quantity)

            except IndexError:
                logging.warning(f"{ticker_symbol}: No Data")
            except Exception as e:
                logging.error(f"Error processing {ticker_symbol}: {e}")

def ema_crossover(ticker_symbol: str):
    stock_info = yf_extender.get_current_stock_data(ticker_symbol)
    if stock_info and 'Close' in stock_info and 'EMA' in stock_info and 'PREVPRICE' in stock_info and 'PREVSMA' in stock_info and (stock_info['Close'] > stock_info['EMA'] and stock_info['PREVPRICE'] < stock_info['PREVSMA'] and stock_info['Close'] > 3):
        print(f"{ticker_symbol} previous price EMA {stock_info['PREVSMA']} previous price {stock_info['PREVPRICE']} current price EMA {stock_info['EMA']} current price {stock_info['Close']}")
        return 0.5
    return 0.0

def trix_strategy(ticker_symbol: str):
    stock_info = yf_extender.get_current_stock_data(ticker_symbol)
    if stock_info and 'TRIX' in stock_info and 'PREVTRIX' in stock_info and 'Close' in stock_info and (stock_info['TRIX'] > 0 and stock_info['PREVTRIX'] <= 0 and stock_info['Close'] > 3):
        print(f"{ticker_symbol} previous TRIX {stock_info['PREVTRIX']} current TRIX {stock_info['TRIX']} current price {stock_info['Close']}")
        return 0.5
    return 0.0

def aroon_strategy(ticker_symbol: str):
    stock_info = yf_extender.get_current_stock_data(ticker_symbol)
    if stock_info and 'AROON_UP' in stock_info and 'AROON_DOWN' in stock_info and 'Close' in stock_info and (stock_info['AROON_UP'] > stock_info['AROON_DOWN'] and stock_info['Close'] > 3):
        print(f"{ticker_symbol} Aroon Up {stock_info['AROON_UP']} Aroon Down {stock_info['AROON_DOWN']} current price {stock_info['Close']}")
        return 0.3
    return 0.0

def elder_ray_strategy(ticker_symbol: str):
    stock_info = yf_extender.get_current_stock_data(ticker_symbol)
    if stock_info and 'BULL_POWER' in stock_info and 'BEAR_POWER' in stock_info and 'Close' in stock_info and (stock_info['BULL_POWER'] > 0 and stock_info['BEAR_POWER'] < 0 and stock_info['Close'] > 3):
        print(f"{ticker_symbol} Bull Power {stock_info['BULL_POWER']} Bear Power {stock_info['BEAR_POWER']} current price {stock_info['Close']}")
        return 0.4
    return 0.0

def evaluate_purchased_stocks():
    time.sleep(2)
    while True:
        purchased_copy = dict(portfolio_manager.purchased)
        for ticker_symbol in purchased_copy:
            stock_info = get_stock_state(ticker_symbol)
            if stock_info is None:
                continue

            price_change_since_purchase = stock_info['Close'] - purchased_copy[ticker_symbol]['Close']
            print(
                (
                    f"Checking {ticker_symbol}"
                    + " | Direction: {0} | Price Change: {1} | Gains/Losses: {2}".format(
                        yf_extender.get_direction(ticker_symbol),
                        price_change_since_purchase,
                        price_change_since_purchase
                        * purchased_copy[ticker_symbol]['Quantity'],
                    )
                )
            )
            if stock_info['Close'] < yf_extender.calculate_ema(ticker_symbol):
                print(f"Because stock price dropped below EMA line, {ticker_symbol}")
                portfolio_manager.sell_stock(ticker_symbol)
                break
            elif yf_extender.get_direction(ticker_symbol) < -0.001:  # should depend on proportion
                print("Because direction is downward {0}".format(
                    yf_extender.get_direction(ticker_symbol)))
                portfolio_manager.sell_stock(ticker_symbol)
                break
            time.sleep(0.1)