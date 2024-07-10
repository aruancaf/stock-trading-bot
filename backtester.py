
from collections import Counter
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
import constants as const
import backtrader as bt
from db_manager import dbHandler

# Load credentials from environment variables
import credentials

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
        self.initial_balance = initial_balance
        self.positions = {}
        self.trades = []
        self.results = []

    def buy_stock(self, ticker, price, date):
        if ticker not in self.positions:
            self.positions[ticker] = {'price': price, 'date': date}
            self.balance -= price
            self.trades.append({'ticker': ticker, 'price': price, 'date': date, 'type': 'buy'})
            logging.info(f"Bought {ticker} at {price} on {date}")

    def sell_stock(self, ticker, price, date):
        if ticker in self.positions:
            self.balance += price
            self.trades.append({'ticker': ticker, 'price': price, 'date': date, 'type': 'sell'})
            del self.positions[ticker]
            logging.info(f"Sold {ticker} at {price} on {date}")

    def run_strategy(self, strategy, tickers):
        for ticker in tickers:
            historical_data_5m_6mo = sdg.get_historical_data(ticker, '6mo', '5m')
            historical_data_4h_6mo = sdg.get_historical_data(ticker, '6mo', '4h')
            historical_data_1m_30d = sdg.get_historical_data(ticker, '30d', '1m')
            historical_data = pd.concat([historical_data_5m_6mo, historical_data_4h_6mo, historical_data_1m_30d])

            for date, row in historical_data.iterrows():
                stock_info = {
                    'Close': row['Close'],
                    'EMA': util.calculate_ema(historical_data),
                    'SMA': util.calculate_moving_average(historical_data),
                    'PREVPRICE': row['Close'],
                    'PREVSMA': util.calculate_moving_average(historical_data),
                    'TRIX': util.calculate_trix(historical_data),
                    'PREVTRIX': util.calculate_trix(historical_data),
                    'AROON_UP': util.calculate_aroon(historical_data),
                    'AROON_DOWN': util.calculate_aroon(historical_data),
                    'BULL_POWER': util.calculate_elder_ray(historical_data),
                    'BEAR_POWER': util.calculate_elder_ray(historical_data),
                    'HEIKIN_ASHI_CLOSE': util.calculate_heikin_ashi(historical_data),
                    'Open': row['Open'],
                    'Close_Prev': row['Close'],
                    'Volume': row['Volume'],
                    'Volume_Prev': row['Volume'],
                    'RSI': util.calculate_rsi(historical_data),
                    'PSAR': util.calculate_parabolic_sar(historical_data)
                }
                signal = strategy(ticker, stock_info)
                if signal == 'buy':
                    self.buy_stock(ticker, row['Close'], date)
                elif signal == 'sell':
                    self.sell_stock(ticker, row['Close'], date)

    def generate_report(self):
        if not self.trades:
            logging.error("No trades were executed.")
            raise ValueError("No trades were executed.")
        
        df = pd.DataFrame(self.trades)
        logging.info(f"Trades DataFrame: \n{df}")

        if 'price' not in df.columns:
            logging.error("The 'price' column is missing in the trades DataFrame.")
            raise KeyError("The 'price' column is missing in the trades DataFrame.")
        if 'date' not in df.columns:
            logging.error("The 'date' column is missing in the trades DataFrame.")
            raise KeyError("The 'date' column is missing in the trades DataFrame.")
        
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df['cumulative_balance'] = self.initial_balance + df['price'].cumsum()

        logging.info(f"Cumulative Balance DataFrame: \n{df}")

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

    def calculate_metrics(self):
        df = pd.DataFrame(self.trades)
        if 'price' not in df.columns or 'date' not in df.columns:
            raise KeyError("The 'price' or 'date' column is missing in the trades DataFrame.")
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        metrics = {
            'Net Performance': self.calculate_performance(),
            'Positions': len(self.positions),
            'Trades': len(self.trades),
        }

        metrics |= self._calculate_streak_metrics(df)
        metrics.update(self._calculate_drawdown_metrics(df))
        metrics.update(self._calculate_performance_metrics(df))
        metrics.update(self._calculate_sharpe_ratio(df))
        metrics.update(self._calculate_sortino_ratio(df))

        self.results.append(metrics)

        return metrics

    def _calculate_streak_metrics(self, df):
        win_streaks, loss_streaks = self._get_streaks(df)
        return {
            'Win Streak, avg': sum(win_streaks) / len(win_streaks) if win_streaks else 0,
            'Win Streak, max': max(win_streaks) if win_streaks else 0,
            'Loss Streak, avg': sum(loss_streaks) / len(loss_streaks) if loss_streaks else 0,
            'Loss Streak, max': max(loss_streaks) if loss_streaks else 0,
        }

    def _calculate_drawdown_metrics(self, df):
        cumulative_returns = df['price'].cumsum()
        drawdown = cumulative_returns.cummax() - cumulative_returns
        return {
            'Max Drawdown': drawdown.max(),
        }

    def _calculate_performance_metrics(self, df):
        wins = df[df['price'] > 0]['price']
        losses = df[df['price'] < 0]['price']
        returns = df['price']

        avg_win = 0 if wins.empty else wins.mean()
        avg_loss = 0 if losses.empty else abs(losses.mean())

        return {
            'Losses': len(losses),
            'Average Win': avg_win,
            'Average Loss': avg_loss,
            'Average Return': 0 if returns.empty else returns.mean(),
            'Reward-to-Risk Ratio': avg_win / avg_loss if avg_loss != 0 else 0,
        }

    def _calculate_sharpe_ratio(self, df, risk_free_rate=0):
        returns = df['price'].cumsum()
        sharpe_ratio = (returns.mean() - risk_free_rate) / returns.std()
        return {'Sharpe (90 days)': sharpe_ratio}

    def _calculate_sortino_ratio(self, df, risk_free_rate=0):
        returns = df['price'].cumsum()
        downside_returns = returns[returns < 0]
        sortino_ratio = (returns.mean() - risk_free_rate) / downside_returns.std()
        return {'Sortino (90 days)': sortino_ratio}

    def _get_streaks(self, df):
        win_streaks = []
        loss_streaks = []
        current_win_streak = 0
        current_loss_streak = 0

        for price in df['price']:
            if price > 0:
                current_win_streak += 1
                if current_loss_streak > 0:
                    loss_streaks.append(current_loss_streak)
                    current_loss_streak = 0
            elif price < 0:
                current_loss_streak += 1
                if current_win_streak > 0:
                    win_streaks.append(current_win_streak)
                    current_win_streak = 0

        if current_win_streak > 0:
            win_streaks.append(current_win_streak)
        if current_loss_streak > 0:
            loss_streaks.append(current_loss_streak)

        return win_streaks, loss_streaks

    def get_results(self):
        return self.results

class StrategyRunner:
    def __init__(self):
        self.strategies = {
            "combined_strategy": self.combined_strategy,
            "moving_average_checker": util.calculate_moving_average,
            "volume_checker": util.calculate_volume,
            "trix_checker": util.calculate_trix,
            "aroon_checker": util.calculate_aroon,
            "elder_ray_checker": util.calculate_elder_ray,
            "heikin_ashi_checker": util.calculate_heikin_ashi,
            "rapid_rebound_checker": util.calculate_rapid_rebound,
            "parabolic_sar_checker": util.calculate_parabolic_sar,
        }

class StrategyRunner:
    def __init__(self):
        self.strategies = {
            "combined_strategy": self.combined_strategy,
            "moving_average_strategy": util.calculate_moving_average,
            "volume_strategy": util.calculate_volume,
            "trix_strategy": util.calculate_trix,
            "aroon_strategy": util.calculate_aroon,
            "elder_ray_strategy": util.calculate_elder_ray,
            "heikin_ashi_strategy": util.calculate_heikin_ashi,
            "rapid_rebound_strategy": util.calculate_rapid_rebound,
            "parabolic_sar_strategy": util.calculate_parabolic_sar,
        }
        self.scores = Counter()
        
    def combined_strategy(self, ticker, stock_info) -> float:
        score = 0
        score += util.calculate_moving_average(stock_info)
        score += util.calculate_volume(stock_info)
        score += util.calculate_trix(stock_info)
        score += util.calculate_aroon(stock_info)
        score += util.calculate_elder_ray(stock_info)
        score += util.calculate_heikin_ashi(stock_info)
        score += util.calculate_rapid_rebound(stock_info)
        score += util.calculate_parabolic_sar(stock_info)
        return score

    def run_backtest(self, start_date, end_date, initial_balance):
        backtester = Backtester(start_date, end_date, initial_balance)
        tickers = scraper.active_stocks() + const.STOCKS_TO_CHECK  # Pull the symbols from the scraper module and constants file
        batches = util.partition_array(tickers, 10)  # Split tickers into batches of 10

        for batch_num, batch in enumerate(batches):
            logging.info(f"Starting backtest for batch {batch_num + 1}/{len(batches)}: {batch}")
            for name, strategy in self.strategies.items():
                backtester.run_strategy(strategy, batch)
                metrics = backtester.calculate_metrics()
                logging.info(f"Backtest metrics for {name} in batch {batch_num + 1}: {metrics}")

                # Determine the best strategy for each metric
                best_strategy = max(metrics, key=metrics.get)
                self.scores[best_strategy] += 1

            logging.info(f"Completed backtest for batch {batch_num + 1}/{len(batches)}")

        best_overall_strategy = max(self.scores, key=self.scores.get)
        logging.info(f"Best overall strategy: {best_overall_strategy} with score: {self.scores[best_overall_strategy]}")
        return backtester.get_results()     
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(filename='backtester.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialize DBManager with credentials from environment variables
    db_credentials = {
        "dbname": credentials.DB_NAME,
        "user": credentials.DB_USER,
        "password": credentials.DB_PASSWORD,
        "host": credentials.DB_HOST,
        "port": credentials.DB_PORT
    }
    db_manager = dbHandler(db_credentials)

    # Running Backtests
    strategy_runner = StrategyRunner()
    start_date = "2019-01-01"
    end_date = "2023-12-31"
    initial_balance = 1000

    # Pulling symbols from constants file and scraper
    tickers = set(scraper.active_stocks() + const.STOCKS_TO_CHECK)

    for _ in tickers:
        strategy_runner.run_backtest(start_date=start_date, end_date=end_date, initial_balance=initial_balance)
        results = strategy_runner.get_results()  # Assuming this method exists to get the results of the backtest
        for result in results:
            db_manager.save_result(result)  # Assuming this method exists to save the result to the database

    # Close DB connection on exit
    db_manager.close()