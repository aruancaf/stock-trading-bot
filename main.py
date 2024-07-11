import os
import timeit
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yahoo_fin.stock_info as si
import strategies as strat
import itertools

class Market:
    data = None
    name = None

    def __init__(self, ticker, beginning, path=0):
        if path != 0:
            self.data = pd.read_csv(path, usecols=['Date', 'Close'])
            self.name = os.path.basename(path).split('/')[-1]
            self.data.set_index('Date', inplace=True)
        else:
            df = si.get_data(ticker, start_date=beginning)
            self.data = df['close']
            self.name = ticker

    def ret(self, first, last):
        return (self.data.iloc[last] - self.data.iloc[first]) / self.data.iloc[first]

    def avgret(self):
        rsum = 0
        for i in range(self.data.size - 1):
            ret = self.ret(i, i + 1)
            rsum += ret
        i += 1
        ret = rsum / i
        return ret

    def sma(self, position, period=5):
        if position - period < 0:
            return 0
        return self.data.iloc[position + 1 - period:position + 1].sum() / period

    def emotion(self, position, threshold=0.1):
        emotion = self.ret(position - 1, position)
        if emotion <= -threshold:
            emotion = 'panic'
        elif emotion >= threshold:
            emotion = 'hype'
        else:
            emotion = 'neutral'
        return emotion

def execute(market, strategy, stratParams=None):
    if stratParams is None:
        stratParams = [0, 0]
    periods = np.zeros(market.data.size)
    for i in range(market.data.size):
        periods[i] = int(i)

    totalTrades = 0
    totalReturn = 0
    results = {
        "periods": periods,
        'dates': market.data.index,
        "trades": [],
        "returns": np.zeros(market.data.size),
        "profits": np.zeros(market.data.size),
        "totalTrades": totalTrades,
        "totalReturn": totalReturn,
    }

    activeTrade = -1
    tradeType = "no position"

    for i in range(market.data.size):
        tradeAction = strategy(market, i, stratParams)
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

def plot_strategy(stock, data, smaParams):
    fastSMA = np.zeros(stock.data.size)
    slowSMA = np.zeros(stock.data.size)
    
    for x in range(stock.data.size):
        fastSMA[x] = stock.sma(x, smaParams[0])
        slowSMA[x] = stock.sma(x, smaParams[1])
    
    plt.plot(data['dates'], stock.data, label='Stock Price')
    plt.plot(data['dates'], fastSMA, '.-g', label=f'SMA{smaParams[0]}')
    plt.plot(data['dates'], slowSMA, '.-y', label=f'SMA{smaParams[1]}')
    
    for x in range(stock.data.size):
        if "short" in data["trades"][x]:
            color = 'red'
        elif "long" in data["trades"][x]:
            color = 'green'
        else:
            color = 'blue'
        
        if "close" in data["trades"][x]:
            plt.annotate(data["trades"][x], xy=(data["dates"][x], fastSMA[x]),
                         xytext=(data["dates"][x], fastSMA[x] + 1),
                         arrowprops=dict(facecolor=color, shrink=0.05))
    
    plt.suptitle(stock.name)
    plt.xlabel("Date")
    plt.ylabel("Stock Price")
    plt.legend()
    
    stockReturn = stock.ret(0, stock.data.size - 1) * 100
    stockReturn = np.around(stockReturn, 2)
    
    plt.text(data['dates'][-200], 0.5,
             f"Buy and Hold Return: {stockReturn}%\n"
             f"SMA{str(smaParams[0])} over SMA{str(smaParams[1])} crossover strategy total return: {data['totalReturn']}%",
             horizontalalignment='center',
             verticalalignment='center')

# MAIN RUN
start_time = timeit.default_timer()
start_date = '01/01/2018'
file_path = '/Users/chefsbae/stock-trading-bot/tickers.xlsx'
tickers = pd.read_excel(file_path)
stocks = [Market(ticker, start_date) for ticker in tickers['tickers'][:5]]
fast = [1, 2, 3, 5, 8, 10, 15, 20]
slow = [2, 3, 5, 8, 10, 15, 20, 50]
stats = {
    'strategy': [],
    'fastsma': [],
    'slowsma': [],
    'fast-slow': [],
    'company': [],
    'returns': [],
    'number of trades': [],
    'company return': []
}

# SMA Crossover Strategy Backtesting
for sma1, sma2 in itertools.product(fast, slow):
    if sma2 <= sma1: continue
    smaParams = [sma1, sma2]

    for stock in stocks:
        start_time2 = timeit.default_timer()
        data = execute(stock, strat.strategySmaCrossover, smaParams)
        print(timeit.default_timer() - start_time2)
        print(sma1, '->', sma2, 'for', stock.name)
        stats['strategy'].append('SMA Crossover')
        stats['fastsma'].append(sma1)
        stats['slowsma'].append(sma2)
        stats['fast-slow'].append(f'{sma1}-{sma2}')
        stats['company'].append(stock.name)
        stats['number of trades'].append(data['totalTrades'])
        stats['returns'].append(data['totalReturn'])
        stats['company return'].append(stock.ret(0, stock.data.size - 1) * 100)

# Mean Reversion Strategy Backtesting
mean_reversion_params = [20, 2]
for stock in stocks:
    start_time2 = timeit.default_timer()
    data = execute(stock, strat.meanReversionStrategy, mean_reversion_params)
    print(timeit.default_timer() - start_time2)
    print('Mean Reversion for', stock.name)
    stats['strategy'].append('Mean Reversion')
    stats['fastsma'].append(None)
    stats['slowsma'].append(None)
    stats['fast-slow'].append(None)
    stats['company'].append(stock.name)
    stats['number of trades'].append(data['totalTrades'])
    stats['returns'].append(data['totalReturn'])
    stats['company return'].append(stock.ret(0, stock.data.size - 1) * 100)

stats = pd.DataFrame(stats)
stats.to_excel('/Users/chefsbae/stock-trading-bot/new_Results.xlsx')
print(timeit.default_timer() - start_time)