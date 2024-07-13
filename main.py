import os
import timeit
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import strategies as strat
import itertools

# Load environment variables
load_dotenv()
QUANDL_API_KEY = os.getenv('QUANDL_API_KEY')

def get_historical_data(symbol):
    url = f"https://data.nasdaq.com/api/v3/datasets/WIKI/{symbol}/data.json?api_key={QUANDL_API_KEY}"
    response = requests.get(url)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    data = response.json()
    dataset = data['dataset_data']
    df = pd.DataFrame(dataset['data'], columns=dataset['column_names'])
    df.set_index('Date', inplace=True)
    return df

def fetch_sp500_list():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    symbols = []
    for row in table.findAll('tr')[1:]:
        symbol = row.findAll('td')[0].text.strip()
        symbols.append(symbol)
    return symbols

class Market:
    data = None
    name = None

    def __init__(self, ticker, beginning, path=0):
        if path != 0:
            self.data = pd.read_csv(path, usecols=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            self.name = os.path.basename(path).split('/')[-1]
            self.data.set_index('Date', inplace=True)
        else:
            df = get_historical_data(ticker)
            if df is None or df.empty:
                raise ValueError(f"No dataset found for symbol {ticker}")
            df = df[df.index >= beginning]
            self.data = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            self.name = ticker

    def ret(self, first, last):
        return (self.data.iloc[last]['Close'] - self.data.iloc[first]['Close']) / self.data.iloc[first]['Close']

    def avgret(self):
        rsum = 0
        for i in range(self.data.shape[0] - 1):
            ret = self.ret(i, i + 1)
            rsum = rsum + ret
        i = i + 1
        ret = rsum / i
        return ret

    def sma(self, position, period=5):
        if position - period < 0:
            return 0
        return self.data['Close'].iloc[position + 1 - period:position + 1].mean()

    def ema(self, position, period=5):
        if position - period < 0:
            return 0
        close_prices = self.data['Close'][:position + 1]
        return close_prices.ewm(span=period, adjust=False).mean().iloc[-1]

    def emotion(self, position, threshold=0.1):
        emotion = self.ret(position - 1, position)
        if emotion <= -threshold:
            emotion = 'panic'
        elif emotion >= threshold:
            emotion = 'hype'
        else:
            emotion = 'neutral'
        return emotion

def execute(market, strategy, stratParams=[0, 0]):
    periods = np.zeros(market.data.shape[0])
    for i in range(market.data.shape[0]):
        periods[i] = int(i)

    totalTrades = 0
    totalReturn = 0
    results = {
        "periods": periods,
        'dates': market.data.index,
        "trades": [],
        "returns": np.zeros(market.data.shape[0]),
        "profits": np.zeros(market.data.shape[0]),
        "totalTrades": totalTrades,
        "totalReturn": totalReturn,
        "emotions": []  # New field to store emotion data
    }

    activeTrade = -1
    tradeType = "no position"

    for i in range(market.data.shape[0]):
        tradeAction = strategy(market, i, stratParams)
        results["emotions"].append(market.emotion(i))  # Store emotion data
        if activeTrade == -1:
            if "long" in tradeAction or "short" in tradeAction:
                results["trades"].append(tradeAction)
                activeTrade = i
                tradeType = tradeAction
            else:
                results["trades"].append(tradeAction)
        elif "long" in tradeType:
            if 'close' in tradeAction:
                ret = market.ret(activeTrade, i) - 0.01
                results["returns"][i] = ret
                results["trades"].append(tradeAction)
                tradeType = 'no position'
                activeTrade = -1
            else:
                results["trades"].append("existing position")
            if "short" in tradeAction:
                tradeType = "short"
                activeTrade = i
        elif "short" in tradeType:
            if 'close' in tradeAction:
                ret = abs(market.ret(activeTrade, i)) - 0.01
                results["returns"][i] = ret
                results["trades"].append(tradeAction)
                tradeType = 'no position'
                activeTrade = -1
            else:
                results["trades"].append("existing position")
            if "long" in tradeAction:
                tradeType = "long"
                activeTrade = i

    for i in results["trades"]:
        if "close" in i:
            results["totalTrades"] += 1

    results["totalProfit"] = np.sum(results["profits"])
    results["totalReturn"] = np.around(sum(results["returns"]) * 100, 2)

    return results

def meanReversionStrategy(market, period, stratParams=None):
    if stratParams is None:
        stratParams = {
            'window': 20,
            'threshold': 2,
            'ma_type': 'sma',
            'stop_loss': 0.05,
            'take_profit': 0.4
        }
    
    window = stratParams['window']
    threshold = stratParams['threshold']
    ma_type = stratParams['ma_type']
    stop_loss = stratParams['stop_loss']
    take_profit = stratParams['take_profit']

    if period < window:
        return 'no position'

    if ma_type == 'sma':
        moving_average = market.sma(period, window)
    elif ma_type == 'ema':
        moving_average = market.data.iloc[:period+1].ewm(span=window, adjust=False).mean().iloc[-1]

    price = market.data['Close'].iloc[period]

    # Buy signal: price is significantly below the moving average
    if price < moving_average - threshold:
        return 'buy'
    
    # Sell signal: price is significantly above the moving average
    elif price > moving_average + threshold:
        return 'sell'
    
    # Stop-loss and take-profit levels
    if market.data['Close'].iloc[period - 1] * (1 - stop_loss) >= price:
        return 'sell'  # Stop-loss triggered
    if market.data['Close'].iloc[period - 1] * (1 + take_profit) <= price:
        return 'sell'  # Take-profit triggered
    
    return 'hold'

# MAIN RUN
start_time = timeit.default_timer()
start_date = '01/01/2013'

# Load tickers from CSV file
tickers = pd.read_csv('TICKERS.csv')

# Use the correct column name
stocks = [Market(ticker, start_date) for ticker in tickers['TICKERS'][:10]]

fast = [1, 2, 3, 5, 8, 10, 15, 20]
slow = [2, 3, 5, 8, 10, 15, 20, 50]

stats = {
    'timestamp': [],
    'strategy': [],
    'fastsma': [],
    'slowsma': [],
    'fast-slow': [],
    'company': [],
    'returns': [],
    'number of trades': [],
    'company return': [],
    'emotions': []  # Added emotions to the stats
}

# SMA Crossover Strategy Backtesting
for sma1, sma2 in itertools.product(fast, slow):
    if sma2 <= sma1: continue
    smaParams = [sma1, sma2]

    for stock in stocks:
        start_time2 = timeit.default_timer()
        data = execute(stock, strat.strategySmaCrossover, smaParams)
        end_time2 = timeit.default_timer()
        timestamp = datetime.datetime.now().isoformat()
        if data:
            print(f"{timestamp}: {sma1} -> {sma2} for {stock.name} in {end_time2 - start_time2} seconds")
            stats['timestamp'].append(timestamp)
            stats['strategy'].append('SMA Crossover')
            stats['fastsma'].append(sma1)
            stats['slowsma'].append(sma2)
            stats['fast-slow'].append(f'{sma1}-{sma2}')
            stats['company'].append(stock.name)
            stats['number of trades'].append(data['totalTrades'])
            stats['returns'].append(data['totalReturn'])
            stats['company return'].append(stock.ret(0, len(stock.data) - 1) * 100)
            stats['emotions'].append(stock.emotion(len(stock.data) - 1))  # Added emotion data

# Mean Reversion Strategy Backtesting
mean_reversion_params = {
    'window': 20,
    'threshold': 2,
    'ma_type': 'sma',
    'stop_loss': 0.05,
    'take_profit': 0.4
}
for stock in stocks:
    start_time2 = timeit.default_timer()
    data = execute(stock, meanReversionStrategy, mean_reversion_params)
    end_time2 = timeit.default_timer()
    timestamp = datetime.datetime.now().isoformat()
    if data:
        print(f"{timestamp}: Mean Reversion for {stock.name} in {end_time2 - start_time2} seconds")
        stats['timestamp'].append(timestamp)
        stats['strategy'].append('Mean Reversion')
        stats['fastsma'].append(None)
        stats['slowsma'].append(None)
        stats['fast-slow'].append(None)
        stats['company'].append(stock.name)
        stats['number of trades'].append(data['totalTrades'])
        stats['returns'].append(data['totalReturn'])
        stats['company return'].append(stock.ret(0, len(stock.data) - 1) * 100)
        stats['emotions'].append(stock.emotion(len(stock.data) - 1))  # Added emotion data

# Saving results
stats_df = pd.DataFrame(stats)
results_file_path = f'new_Results_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
stats_df.to_excel(results_file_path, index=False)
print(f"Results saved to {results_file_path}")
print(timeit.default_timer() - start_time)
print("Done")

# Group by strategy and calculate the mean and sum of returns
strategy_performance = stats_df.groupby('strategy')['returns'].agg(['mean', 'sum'])

# Print the results
print(strategy_performance)