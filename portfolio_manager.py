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
    purchased_copy = dict(purchased)

    if ticker_symbol not in purchased_copy and buying_power >= (quantity * yf_ext.get_stock_state(ticker)['Close']):
        stock_info = yf_ext.get_stock_state(ticker)
        stock_info['Quantity'] = quantity
        purchased[ticker_symbol] = stock_info
        console_output = "Buying " + ticker_symbol + "\n"
        print(console_output, end=' ')
        buying_power -= (quantity * yf_ext.get_stock_state(ticker)['Close'])
        alerts.sayBeep(1)

    json_simp.updated_purchased()
    json_simp.read_json()


def sell_stock(ticker: yf.Ticker):
    global buying_power
    ticker_symbol = yf_ext.get_ticker_symbol(ticker)
    refresh_account()

    sold_copy = dict(sold)
    purchased_copy = dict(purchased)
    if ticker_symbol not in sold_copy:
        stock_info = Counter(yf_ext.get_stock_state(ticker))
        purchase_info = Counter(purchased.pop(ticker_symbol))
        stock_info.pop('Time')
        purchase_info.pop('Time')
        stock_info.subtract(purchase_info)
        stock_info['Time'] = datetime.now().strftime("%H:%M:%S")
        sold[ticker_symbol] = stock_info
        buying_power += stock_info['Close'] * abs(stock_info['Quantity'])

    elif ticker_symbol in purchased_copy:
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
    console_output = "Selling " + ticker_symbol + "\n"
    print(console_output, end=' ')
    alerts.sayBeep(2)


def refresh_account():
    global buying_power
    global account_value
    json_simp.read_json()

    buying_power = trading_constants.starting_account_value
    account_value = trading_constants.starting_account_value
    purchased_copy = dict(purchased)
    sold_copy = dict(sold)

    for ticker_symbol in purchased_copy:
        buying_power -= purchased[ticker_symbol]['Close'] * purchased[ticker_symbol]['Quantity']
        account_value += yf_ext.get_stock_state(yf.Ticker(ticker_symbol))['Close'] - purchased[ticker_symbol]['Close']

    for ticker_symbol in sold_copy:
        temp = sold[ticker_symbol]['Close'] * abs(sold[ticker_symbol]['Quantity'])
        buying_power += temp
        account_value += temp


def print_account_status():
    refresh_account()
    print("Buying Power {0}".format((buying_power*1000)/1000))
    print("Account Value {0}".format((account_value*1000)/1000))
