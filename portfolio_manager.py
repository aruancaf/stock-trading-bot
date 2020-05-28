from collections import Counter
from datetime import datetime

import yfinance as yf

import trading_constants
import utils.json_simplifier as json_simp
import yf_extender as yf_ext
from utils import alerts

purchased = {}
sold = {}
buying_power = trading_constants.starting_account_value
account_value = trading_constants.starting_account_value




def buy_stock(ticker: yf.Ticker, quantity: int):
    global buying_power
    ticker_symbol = yf_ext.get_ticker_symbol(ticker)
    json_simp.read_json()
    refresh_account()

    if ticker_symbol not in purchased and buying_power >= (quantity * yf_ext.get_stock_state(ticker)['Close']):
        stock_info = yf_ext.get_stock_state(ticker)
        stock_info['Quantity'] = quantity
        purchased[ticker_symbol] = stock_info
        print("Buying", ticker_symbol)
        buying_power -= (quantity * yf_ext.get_stock_state(ticker)['Close'])
        alerts.sayBeep(1)

    json_simp.updated_purchased()
    json_simp.read_json()


def sell_stock(ticker: yf.Ticker):
    global buying_power
    ticker_symbol = yf_ext.get_ticker_symbol(ticker)
    refresh_account()

    if ticker_symbol not in sold:
        stock_info = Counter(yf_ext.get_stock_state(ticker))
        purchase_info = Counter(purchased.pop(ticker_symbol))
        stock_info.pop('Time')
        purchase_info.pop('Time')
        stock_info.subtract(purchase_info)
        stock_info['Time'] = datetime.now().strftime("%H:%M:%S")
        sold[ticker_symbol] = stock_info
        buying_power += stock_info['Close'] * abs(stock_info['Quantity'])

    elif ticker_symbol in purchased:
        stock_info = Counter(yf_ext.get_stock_state(ticker))
        purchase_info = Counter(purchased.pop(ticker_symbol))
        sold_info = Counter(sold.pop(ticker_symbol))
        stock_info.pop('Time')
        purchase_info.pop('Time')
        sold_info.pop('Time')
        stock_info.subtract(purchase_info)

        for i in stock_info and sold_info:
            stock_info[i] = stock_info[i] + sold_info[i]
        stock_info['Time'] = datetime.now().strftime("%H:%M:%S")
        sold[ticker_symbol] = stock_info
        buying_power += stock_info['Close'] * abs(stock_info['Quantity'])

    json_simp.updated_purchased()
    json_simp.updated_sold()
    json_simp.read_json()
    print("Selling", ticker_symbol)
    alerts.sayBeep(2)


def refresh_account():
    global buying_power
    global account_value
    json_simp.read_json()

    buying_power = trading_constants.starting_account_value
    account_value = trading_constants.starting_account_value

    for ticker_symbol in purchased:
        buying_power -= purchased[ticker_symbol]['Close'] * purchased[ticker_symbol]['Quantity']

    for ticker_symbol in sold:
        temp = sold[ticker_symbol]['Close'] * abs(sold[ticker_symbol]['Quantity'])
        buying_power += temp
        account_value += temp


def print_account_status():
    refresh_account()
    print("Buying Power {0}".format(buying_power))
    print("Account Value {0}".format(account_value))
