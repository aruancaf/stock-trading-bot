import threading
from collections import Counter
from datetime import datetime
import alpaca_trade_api as tradeapi
import yfinance as yf
import trading_constants
import utils.json_simplifier as json_simp
import yf_extender as yf_ext
from utils import alerts

# Directly set the Alpaca API keys here
ALPACA_API_KEY = "PKH65BIUK3JXOKTG9FFP"
ALPACA_SECRET_KEY = "09tdgkypsnIoKGCQULcJKvx9g9qZFurtXvaHlBH3"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets/v2"

# Alpaca Dashboard: https://app.alpaca.markets/paper/dashboard/overview

def initializeApAccount():
    global api
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=ALPACA_BASE_URL)

purchased = {}
sold = {}
buying_power = trading_constants.starting_account_value
account_value = trading_constants.starting_account_value
transaction_history = []
alerts_list = []
lock = threading.Lock()

def buy_stock(ticker_symbol: str, quantity: int):
    with lock:
        global buying_power
        json_simp.read_json()
        purchased_copy = dict(purchased)
        ticker = yf.Ticker(ticker_symbol)
        stock_info = yf_ext.get_stock_state(ticker)

        if ticker_symbol not in purchased_copy and buying_power > (quantity * stock_info['Close']):
            api.submit_order(
                symbol=ticker_symbol,
                qty=quantity,
                side='buy',
                type='market',
                time_in_force='day'
            )
            stock_info['Quantity'] = quantity
            purchased[ticker_symbol] = stock_info
            console_output = (
                f"Buying {ticker_symbol}"
                + " Quantity: {0}".format(stock_info['Quantity'])
                + "\n"
            )
            print(console_output, end=' ')
            buying_power -= (quantity * yf_ext.get_stock_state(ticker)['Close'])
            alerts.say_beep(1)
            transaction_history.append({
                "type": "buy",
                "symbol": ticker_symbol,
                "quantity": quantity,
                "price": stock_info['Close'],
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        json_simp.updated_purchased()
        json_simp.read_json()

def sell_stock(ticker_symbol: str):
    api.close_position(ticker_symbol)
    global buying_power
    refresh_account_balance()
    sold_copy = dict(sold)
    ticker = yf.Ticker(ticker_symbol)
    stock_info = Counter(yf_ext.get_stock_state(ticker))
    purchased_copy = dict(purchased)
    console_output = (
        f"Selling {ticker_symbol}"
        + " Quantity: {0}".format(stock_info['Quantity'])
        + "\n"
    )

    if ticker_symbol not in sold_copy and ticker_symbol != "":
        purchase_info = Counter(purchased.pop(ticker_symbol))
        console_output = (
            f"Selling {ticker_symbol}"
            + " Quantity: {0}".format(purchase_info['Quantity'])
            + "\n"
        )
        stock_info.pop('Time')
        purchase_info.pop('Time')
        stock_info.subtract(purchase_info)
        _extracted_from_sell_stock_25(
            stock_info, ticker_symbol, buying_power, purchase_info
        )
    elif ticker_symbol in purchased_copy:
        purchase_info = Counter(purchased.pop(ticker_symbol))
        console_output = (
            f"Selling {ticker_symbol}"
            + " Quantity: {0}".format(purchase_info['Quantity'])
            + "\n"
        )
        sold_info = Counter(sold.pop(ticker_symbol))
        stock_info.pop('Time')
        purchase_info.pop('Time')
        sold_info.pop('Time')
        stock_info.subtract(purchase_info)

        for I in stock_info and sold_info:
            stock_info[I] = stock_info[I] + sold_info[I]
        _extracted_from_sell_stock_25(
            stock_info, ticker_symbol, buying_power, purchase_info
        )
    json_simp.updated_purchased()
    json_simp.updated_sold()
    json_simp.read_json()
    print(console_output, end=' ')
    alerts.say_beep(2)

# TODO Rename this here and in `sell_stock`
def _extracted_from_sell_stock_25(stock_info, ticker_symbol, buying_power, purchase_info):
    stock_info['Time'] = datetime.now().strftime("%H:%M:%S")
    sold[ticker_symbol] = stock_info
    buying_power += stock_info['Close'] * abs(stock_info['Quantity'])
    transaction_history.append({
        "type": "sell",
        "symbol": ticker_symbol,
        "quantity": purchase_info['Quantity'],
        "price": stock_info['Close'],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def refresh_account_balance():
    with lock:
        global buying_power
        global account_value
        json_simp.read_json()

        buying_power = trading_constants.starting_account_value
        account_value = trading_constants.starting_account_value
        purchased_copy = dict(purchased)
        sold_copy = dict(sold)

        for ticker_symbol in purchased_copy:
            current_ticker_price = yf_ext.get_stock_state(yf.Ticker(ticker_symbol))['Close']
            purchased_ticker_price = purchased_copy[ticker_symbol]['Close']
            purchased_ticker_quantity = purchased_copy[ticker_symbol]['Quantity']
            account_value += current_ticker_price - purchased_ticker_price
            buying_power -= purchased_ticker_price * purchased_ticker_quantity

        for ticker_symbol in sold_copy:
            temp = sold[ticker_symbol]['Close'] * abs(sold[ticker_symbol]['Quantity'])
            buying_power += temp
            account_value += temp

def print_account_status():
    refresh_account_balance()
    print("Buying Power {0}".format((buying_power * 1000) / 1000))
    print("Account Value {0}".format((account_value * 1000) / 1000))

def calculate_total_value(purchased):
    return sum(stock['Close'] * stock['Quantity'] for stock in purchased.values())

def calculate_total_invested(purchased):
    return sum(stock['Close'] * stock['Quantity'] for stock in purchased.values())

def calculate_current_balance(purchased):
    total_value = calculate_total_value(purchased)
    total_invested = calculate_total_invested(purchased)
    return total_value - total_invested

def calculate_profit_loss(purchased):
    total_value = calculate_total_value(purchased)
    total_invested = calculate_total_invested(purchased)
    return total_value - total_invested

def get_transaction_history():
    return transaction_history

def get_alerts():
    return alerts_list

def add_alert(symbol, alert_message, date):
    alerts_list.append({
        "symbol": symbol,
        "alert": alert_message,
        "date": date
    })

# Initialize Alpaca Account
initializeApAccount()