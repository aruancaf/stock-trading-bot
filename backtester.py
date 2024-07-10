import pandas as pd
import stock_data_gatherer as sdg
import stock_analysis as sa
import util
import scraper
import matplotlib.pyplot as plt
import logging
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
from typing import Dict, Any

class PositionSizer:
    def __init__(self, risk_per_trade=0.01, max_leverage=1.0):
        self.risk_per_trade = risk_per_trade
        self.max_leverage = max_leverage

    def calculate_position_size(self, portfolio_value, price):
        position_size = (portfolio_value * self.risk_per_trade) / price
        return min(position_size, self.max_leverage * portfolio_value / price)

class Backtester:
    def __init__(self, start_date, end_date, initial_balance=1000):
        self.start_date = start_date
        self.end_date = end_date
        self.balance = initial_balance
        self.positions = {}
        self.trades = []

    def buy_stock(self, ticker, price, date):
        if ticker not in self.positions:
            self.positions[ticker] = {'price': price, 'date': date}
            self.balance -= price
            self.trades.append({'ticker': ticker, 'price': price, 'date': date, 'type': 'buy'})

    def sell_stock(self, ticker, price, date):
        if ticker in self.positions:
            self.balance += price
            self.trades.append({'ticker': ticker, 'price': price, 'date': date, 'type': 'sell'})
            del self.positions[ticker]

    def run_strategy(self, strategy, tickers):
        for ticker in tickers:
            historical_data = sdg.get_historical_data(ticker, '5y', '1d')  # Adjust the period and interval as needed
            for date, row in historical_data.iterrows():
                stock_info = {
                    'Close': row['Close'],
                    'EMA': row.get('EMA'),
                    'SMA': row.get('SMA'),
                    'PREVPRICE': row.get('PREVPRICE'),
                    'PREVSMA': row.get('PREVSMA'),
                    'TRIX': row.get('TRIX'),
                    'PREVTRIX': row.get('PREVTRIX'),
                    'AROON_UP': row.get('AROON_UP'),
                    'AROON_DOWN': row.get('AROON_DOWN'),
                    'BULL_POWER': row.get('BULL_POWER'),
                    'BEAR_POWER': row.get('BEAR_POWER'),
                    'HEIKIN_ASHI_CLOSE': row.get('HEIKIN_ASHI_CLOSE'),
                    'Open': row['Open'],
                    'Close_Prev': row.get('Close_Prev'),
                    'Volume': row['Volume'],
                    'Volume_Prev': row.get('Volume_Prev'),
                    'RSI': row.get('RSI'),
                    'PSAR': row.get('PSAR')
                }
                signal = strategy(ticker, stock_info)
                if signal == 'buy':
                    self.buy_stock(ticker, row['Close'], date)
                elif signal == 'sell':
                    self.sell_stock(ticker, row['Close'], date)

    def calculate_metrics(self):
        df = pd.DataFrame(self.trades)
        if 'date' not in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        net_performance = self.balance + sum(
            position['price'] for position in self.positions.values()
        )
        return {
            'Net Performance': net_performance,
            'Positions': len(self.positions),
            # Add other metrics as needed
        }

    def generate_report(self):
        df = pd.DataFrame(self.trades)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df['cumulative_balance'] = self.balance + df['price'].cumsum()

        print(df)

        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df['cumulative_balance'], label='Cumulative Balance')
        plt.xlabel('Date')
        plt.ylabel('Balance')
        plt.title('Backtesting Results')
        plt.legend()
        plt.show()

    def calculate_performance(self):
        final_balance = self.balance + sum(
            position['price'] for position in self.positions.values()
        )
        self.generate_report()
        return final_balance

class StrategyRunner:
    def __init__(self):
        self.strategies = {
            "combined_strategy": sa.combined_strategy,
            # Add other strategies if needed
        }

    def run_backtest(self, start_date, end_date, initial_balance):
        logging.info("Starting backtest from %s to %s", start_date, end_date)
        backtester = Backtester(start_date, end_date, initial_balance)
        tickers = scraper.active_stocks()  # Pull the symbols from the scraper module
        partitioned_tickers = util.partition_array(tickers, 10)  # Ensure each batch is under 10 symbols
        strategy_metrics = {}
        
        for batch in partitioned_tickers:
            for name, strategy in self.strategies.items():
                logging.info("Running strategy: %s on batch: %s", name, batch)
                backtester.run_strategy(strategy, batch)
                strategy_metrics[name] = backtester.calculate_metrics()
                logging.info("Finished strategy: %s on batch: %s with metrics: %s", name, batch, strategy_metrics[name])
        
        logging.info("Completed backtest")
        return strategy_metrics

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(filename='backtester.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Running Backtests
    strategy_runner = StrategyRunner()
    strategy_runner.run_backtest(start_date="2019-01-01", end_date="2023-12-31", initial_balance=1000)