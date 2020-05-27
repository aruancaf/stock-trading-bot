from collections import Counter
from datetime import datetime

import yfinance as yf

import utils.json_simplifier as json_simpl
import yf_extender as yf_ext

purchased = {}
sold = {}


def buy_stock(ticker: yf.Ticker):
    ticker_symbol = yf_ext.get_ticker_symbol(ticker)
    json_simpl.read_json()

    if ticker_symbol not in purchased:
        purchased[ticker_symbol] = yf_ext.get_stock_info(ticker)
    json_simpl.updated_purchased()
    json_simpl.read_json()
    print("Buying", ticker_symbol)


def sell_stock(ticker: yf.Ticker):
    ticker_symbol = yf_ext.get_ticker_symbol(ticker)
    json_simpl.read_json()

    if ticker_symbol not in sold:
        stock_info = Counter(yf_ext.get_stock_info(ticker))
        purchase_info = Counter(purchased.pop(ticker_symbol))
        stock_info.pop('Time')
        purchase_info.pop('Time')
        stock_info.subtract(purchase_info)
        stock_info['Time'] = datetime.now().strftime("%H:%M:%S")
        sold[ticker_symbol] = stock_info

    else:
        stock_info = Counter(yf_ext.get_stock_info(ticker))
        purchase_info = Counter(purchased.pop(ticker_symbol))
        sold_info = Counter(sold.pop(ticker_symbol))
        stock_info.pop('Time')
        purchase_info.pop('Time')
        sold_info.pop('Time')
        print(stock_info)
        print(purchase_info)
        stock_info.subtract(purchase_info)
        print(stock_info)

        for i in stock_info and sold_info:
            stock_info[i] = stock_info[i] + sold_info[i]
        stock_info['Time'] = datetime.now().strftime("%H:%M:%S")
        sold[ticker_symbol] = stock_info

    json_simpl.updated_purchased()
    json_simpl.updated_sold()
    json_simpl.read_json()
    print("Selling", ticker_symbol)

# def get_position_polarity() -> float:


# def get_adjusted_position_polarity():
