import os
import timeit
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yahoo_fin.stock_info as si
import strategies as strat
import itertools
from dotenv import load_dotenv
import httpx
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(filename='market_data.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Load environment variables
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
MORNINGSTAR_API_KEY = os.getenv('MORNINGSTAR_API_KEY')
QUANDL_API_KEY = os.getenv('QUANDL_API_KEY')

# Fetch data from Finnhub
def fetch_finnhub_data(ticker, start_date, end_date):
    try:
        url = f'https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&from={start_date}&to={end_date}&token={FINNHUB_API_KEY}'
        response = httpx.get(url)
        response.raise_for_status()
        data = response.json()

        if 's' in data and data['s'] == 'ok':
            df = pd.DataFrame({
                'Date': pd.to_datetime(data['t'], unit='s'),
                'Open': data['o'],
                'Close': data['c']
            })
            df['SMA'] = df['Close'].rolling(window=20).mean()  # Example for 20-period SMA
            df['EMA'] = df['Close'].ewm(span=20, adjust=False).mean()  # Example for 20-period EMA
            df.set_index('Date', inplace=True)
            return df
        else:
            logging.error(f"Error fetching data for {ticker} from Finnhub")
            return None
    except Exception as e:
        logging.error(f"Exception occurred while fetching data from Finnhub for {ticker}: {e}")
        return None

def fetch_morningstar_data(ticker, start_date, end_date):
    try:
        MORNINGSTAR_API_ENDPOINT = os.getenv('MORNINGSTAR_API_ENDPOINT')
        url = f'{MORNINGSTAR_API_ENDPOINT}/v1/stock/candle?symbol={ticker}&resolution=D&from={start_date}&to={end_date}&token={MORNINGSTAR_API_KEY}'
        response = httpx.get(url)
        response.raise_for_status()
        data = response.json()

        if 's' in data and data['s'] == 'ok':
            df = pd.DataFrame({
                'Date': pd.to_datetime(data['t'], unit='s'),
                'Open': data['o'],
                'Close': data['c']
            })
            df['SMA'] = df['Close'].rolling(window=20).mean()  # Example for 20-period SMA
            df['EMA'] = df['Close'].ewm(span=20, adjust=False).mean()  # Example for 20-period EMA
            df.set_index('Date', inplace=True)
            return df
        else:
            logging.error(f"Error fetching data for {ticker} from Morningstar")
            return None
    except Exception as e:
        logging.error(f"Exception occurred while fetching data from Morningstar for {ticker}: {e}")
        return None

def fetch_alpha_vantage_data(ticker):
    try:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}&outputsize=full'
        response = httpx.get(url)
        response.raise_for_status()
        data = response.json()

        if 'Time Series (Daily)' in data:
            df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.rename(columns={
                '1. open': 'Open',
                '5. adjusted close': 'Close'
            })
            df['SMA'] = df['Close'].rolling(window=20).mean()  # Example for 20-period SMA
            df['EMA'] = df['Close'].ewm(span=20, adjust=False).mean()  # Example for 20-period EMA
            df = df[['Open', 'Close', 'SMA', 'EMA']]
            return df
        else:
            logging.error(f"Error fetching data for {ticker} from Alpha Vantage")
            return None
    except Exception as e:
        logging.error(f"Exception occurred while fetching data from Alpha Vantage for {ticker}: {e}")
        return None

# Market class
class Market:
    data = None
    name = None

    def __init__(self, ticker, beginning, source='finnhub', path=0):
        try:
            if path != 0:
                self.data = pd.read_csv(path, usecols=['Date', 'Close'])
                self.name = os.path.basename(path).split('/')[-1]
                self.data.set_index('Date', inplace=True)
            else:
                if source == 'finnhub':
                    self.data = fetch_finnhub_data(ticker, beginning, int(datetime.datetime.now().timestamp()))
                elif source == 'alpha_vantage':
                    self.data = fetch_alpha_vantage_data(ticker)
                else:
                    raise ValueError(f"Unsupported data source: {source}")

                self.name = ticker

            if self.data is None or self.data.empty:
                raise ValueError(f"No data found for {ticker}")
        except Exception as e:
            logging.error(f"Exception occurred while initializing Market for {ticker}: {e}")

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

# Execute function with logging trade dates
def execute(market, strategy, stratParams=None):
    try:
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
            "trade_dates": [],
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
                    results["trade_dates"].append(market.data.index[i])
                    activeTrade = i
                    tradeType = tradeAction
                else:
                    results["trades"].append(tradeAction)
                    results["trade_dates"].append(None)
            elif "long" in tradeType:
                if 'close' in tradeAction:
                    ret = market.ret(activeTrade, i) - 0.01
                    results["returns"][i] = ret
                    results["trades"].append(tradeAction)
                    results["trade_dates"].append(market.data.index[i])
                    tradeType = 'no position'
                    activeTrade = -1
                else:
                    results["trades"].append("existing position")
                    results["trade_dates"].append(None)
                if "short" in tradeAction:
                    tradeType = "short"
                    activeTrade = i
            elif "short" in tradeType:
                if 'close' in tradeAction:
                    ret = abs(market.ret(activeTrade, i)) - 0.01
                    results["returns"][i] = ret
                    results["trades"].append(tradeAction)
                    results["trade_dates"].append(market.data.index[i])
                    tradeType = 'no position'
                    activeTrade = -1
                else:
                    results["trades"].append("existing position")
                    results["trade_dates"].append(None)
                if "long" in tradeAction:
                    tradeType = "long"
                    activeTrade = i

        for i in results["trades"]:
            if "close" in i:
                results["totalTrades"] += 1

        results["totalProfit"] = np.sum(results["profits"])
        results["totalReturn"] = np.around(sum(results["returns"]) * 100, 2)

        return results
    except Exception as e:
        logging.error(f"Exception occurred during execution: {e}")
        return None

# Plot strategy function
def plot_strategy(stock, data, smaParams):
    try:
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
    except Exception as e:
        print(f"Exception occurred while plotting strategy: {e}")


# MAIN RUN
    try:
        start_time = timeit.default_timer()
        start_date = '01/01/2018'
        file_path = '/Users/chefsbae/stock-trading-bot/tickers.xlsx'
        tickers = pd.read_excel(file_path)
        
        stocks = []
        for ticker in tickers['tickers']:
            try:
                sources = ['finnhub', 'alpha_vantage', 'morningstar']
                stock = None
                for source in sources:
                    if source == 'finnhub':
                        stock = fetch_finnhub_data(ticker, start_date, int(datetime.datetime.now().timestamp()))
                    elif source == 'alpha_vantage':
                        stock = fetch_alpha_vantage_data(ticker)
                    elif source == 'morningstar':
                        stock = fetch_morningstar_data(ticker, start_date, int(datetime.datetime.now().timestamp()))
                    
                    if stock is not None and not stock.empty:
                        stocks.append((ticker, stock))
                        break
                    else:
                        logging.info(f"No valid data for ticker {ticker} from {source}, trying next source.")
                if stock is None or stock.empty:
                    logging.error(f"No valid data found for ticker {ticker} after trying all sources, skipping.")
            except Exception as e:
                logging.error(f"Exception occurred while initializing Market for {ticker}: {e}")
        
        fast = [1, 2, 3, 5, 8, 10, 15, 20]
        slow = [2, 3, 5, 8, 10, 15, 20, 50]
        stats = {
            'timestamp': [],
            'strategy': [],
            'fastsma': [],
            'slowsma': [],
            'fast-slow': [],
            'company': [],
            'trade_dates': [],  # Added trade dates to the stats dictionary
            'returns': [],
            'number of trades': [],
            'company return': []
        }

        # SMA Crossover Strategy Backtesting
        for sma1, sma2 in itertools.product(fast, slow):
            if sma2 <= sma1: continue
            smaParams = [sma1, sma2]

            for ticker, stock in stocks:
                try:
                    start_time2 = timeit.default_timer()
                    data = execute(stock, strat.strategySmaCrossover, smaParams)
                    end_time2 = timeit.default_timer()
                    timestamp = datetime.datetime.now().isoformat()
                    if data:
                        print(f"{timestamp}: {sma1} -> {sma2} for {ticker} in {end_time2 - start_time2} seconds")
                        stats['timestamp'].append(timestamp)
                        stats['strategy'].append('SMA Crossover')
                        stats['fastsma'].append(sma1)
                        stats['slowsma'].append(sma2)
                        stats['fast-slow'].append(f'{sma1}-{sma2}')
                        stats['company'].append(ticker)
                        stats['trade_dates'].append(data['trade_dates'])  # Store trade dates
                        stats['number of trades'].append(data['totalTrades'])
                        stats['returns'].append(data['totalReturn'])
                        stats['company return'].append(stock['Close'].iloc[0] * 100)
                    else:
                        logging.warning(f"Execution failed for {ticker} with SMA params {sma1}-{sma2}")
                except Exception as e:
                    logging.error(f"Exception occurred during SMA Crossover Strategy for {ticker}: {e}")

        # Mean Reversion Strategy Backtesting
        mean_reversion_params = [20, 2]
        for ticker, stock in stocks:
            try:
                start_time2 = timeit.default_timer()
                data = execute(stock, strat.meanReversionStrategy, mean_reversion_params)
                end_time2 = timeit.default_timer()
                timestamp = datetime.datetime.now().isoformat()
                if data:
                    print(f"{timestamp}: Mean Reversion for {ticker} in {end_time2 - start_time2} seconds")
                    stats['timestamp'].append(timestamp)
                    stats['strategy'].append('Mean Reversion')
                    stats['fastsma'].append(None)
                    stats['slowsma'].append(None)
                    stats['fast-slow'].append(None)
                    stats['company'].append(ticker)
                    stats['trade_dates'].append(data['trade_dates'])  # Store trade dates
                    stats['number of trades'].append(data['totalTrades'])
                    stats['returns'].append(data['totalReturn'])
                    stats['company return'].append(stock['Close'].iloc[0] * 100)
                else:
                    logging.warning(f"Execution failed for {ticker} during Mean Reversion Strategy")
            except Exception as e:
                logging.error(f"Exception occurred during Mean Reversion Strategy for {ticker}: {e}")
                
        if len(stats['timestamp']) == len(stats['strategy']) == len(stats['fastsma']) == len(stats['slowsma']) == len(stats['fast-slow']) == len(stats['company']) == len(stats['trade_dates']) == len(stats['returns']) == len(stats['number of trades']) == len(stats['company return']):
            stats_df = pd.DataFrame(stats)
            results_file_path = f'/Users/chefsbae/stock-trading-bot/new_Results_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            stats_df.to_excel(results_file_path, index=False)
            print(f"Results saved to {results_file_path}")
        else:
            print("Stats arrays have different lengths. Unable to save results.")
    except Exception as e:
        logging.error(f"Exception occurred in main run: {e}")

        print(timeit.default_timer() - start_time)
        print("Done")