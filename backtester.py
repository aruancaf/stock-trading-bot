import os
import time
from matplotlib import pyplot as plt
import pandas as pd
import sqlite3
import logging
import psutil
from db_manager import dbHandler
from data_middleman import get_historical_data
import scraper
import util
from collections import Counter
from stock_data_gatherer import get_all_tickers
import multiprocessing as mp
import cProfile
import pstats

logging.basicConfig(filename='backtester.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_system_usage():
    logging.info(f"CPU usage: {psutil.cpu_percent()}%")
    logging.info(f"Memory usage: {psutil.virtual_memory().percent}%")

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

    def buy_stock(self, ticker, price, date):
        logging.info(f"Trying to buy {ticker} at {price} on {date}")
        if ticker not in self.positions:
            self.positions[ticker] = {'price': price, 'date': date}
            self.balance -= price
            self.trades.append({'ticker': ticker, 'price': price, 'date': date, 'type': 'buy'})
            logging.info(f"Bought {ticker} at {price} on {date}")

    def sell_stock(self, ticker, price, date):
        logging.info(f"Trying to sell {ticker} at {price} on {date}")
        if ticker in self.positions:
            self.balance += price
            self.trades.append({'ticker': ticker, 'price': price, 'date': date, 'type': 'sell'})
            del self.positions[ticker]
            logging.info(f"Sold {ticker} at {price} on {date}")

    def generate_report(self):
        if not self.trades:
            raise ValueError("No trades were executed.")
        df = self._extracted_from_calculate_metrics_4()
        df['cumulative_balance'] = self.initial_balance + df['price'].cumsum()

        print(df)

        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df['cumulative_balance'], label='Cumulative Balance')
        plt.xlabel('Date')
        plt.ylabel('Balance')
        plt.title('Backtesting Results')
        plt.legend()
        plt.show()

    def calculate_performance(self):
        logging.info("Calculating performance")
        final_balance = self.balance + sum(
            position['price'] for position in self.positions.values()
        )
        self.generate_report()
        return final_balance

    def calculate_metrics(self):
        logging.info("Calculating metrics")
        df = self._extracted_from_calculate_metrics_4()
        metrics = {
            'Net Performance': self.calculate_performance(),
            'Positions': len(self.positions),
            'Trades': len(self.trades),
        }

        metrics |= self._calculate_streak_metrics(df)
        metrics.update(self._calculate_drawdown_metrics(df))
        metrics.update(self._calculate_performance_metrics(df))

        return metrics

    def _extracted_from_calculate_metrics_4(self):
        result = pd.DataFrame(self.trades)
        if 'price' not in result.columns or 'date' not in result.columns:
            raise KeyError(
                "The 'price' or 'date' column is missing in the trades DataFrame."
            )
        result['date'] = pd.to_datetime(result['date'])
        result.set_index('date', inplace=True)
        return result

    def _calculate_streak_metrics(self, df):
        logging.info("Calculating streak metrics")
        win_streaks, loss_streaks = self._get_streaks(df)
        return {
            'Win Streak, avg': sum(win_streaks) / len(win_streaks) if win_streaks else 0,
            'Win Streak, max': max(win_streaks) if win_streaks else 0,
            'Loss Streak, avg': sum(loss_streaks) / len(loss_streaks) if loss_streaks else 0,
            'Loss Streak, max': max(loss_streaks) if loss_streaks else 0,
        }

    def _calculate_drawdown_metrics(self, df):
        logging.info("Calculating drawdown metrics")
        cumulative_returns = df['price'].cumsum()
        drawdown = cumulative_returns.cummax() - cumulative_returns
        return {
            'Max Drawdown': drawdown.max(),
        }

    def _calculate_performance_metrics(self, df):
        logging.info("Calculating performance metrics")
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

    def _get_streaks(self, df):
        logging.info("Calculating win/loss streaks")
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

class StrategyRunner:
    def __init__(self):
        self.strategies = {
            "combined_strategy": self.combined_strategy,
            "moving_average_strategy": util.calculate_sma,
            "volume_strategy": util.calculate_volume,
            "trix_strategy": util.calculate_trix,
            "aroon_strategy": util.calculate_aroon,
            "elder_ray_strategy": util.calculate_elder_ray,
            "heikin_ashi_strategy": util.calculate_heikin_ashi,
            "rapid_rebound_strategy": util.calculate_rapid_rebound,
            "parabolic_sar_strategy": util.calculate_parabolic_sar,
        }
        self.scores = Counter()
        self.results = []  # List to store results of backtests

    def combined_strategy(self, stock_info) -> float:
        score = 0
        historical_data = stock_info['historical_data']
        open_price = historical_data['open']
        high = historical_data['high']
        low = historical_data['low']
        close = historical_data['close']

        # Use the historical data DataFrame for calculations
        sma_values = util.calculate_sma(historical_data)
        if sma_values[0] is not None:
            score += sma_values[0]
        
        score += util.calculate_volume(historical_data)
        
        trix_value = util.calculate_trix(close)
        if trix_value is not None:
            score += trix_value
        
        aroon_up, aroon_down = util.calculate_aroon(high, low)
        if aroon_up is not None:
            score += aroon_up
        
        bull_power, bear_power = util.calculate_elder_ray(high, low, close)
        if bull_power is not None:
            score += bull_power
        
        heikin_ashi_close = util.calculate_heikin_ashi(open_price, high, low, close)
        if heikin_ashi_close is not None:
            score += heikin_ashi_close
        
        psar_value = util.calculate_parabolic_sar(close, low, high)
        if psar_value is not None:
            score += psar_value
        
        rsi_value = util.calculate_rsi(close)
        if rsi_value is not None:
            score += rsi_value
        
        return score

    def run_strategy(self, strategy, ticker):
        logging.info(f"Fetching historical data for {ticker}")
        try:
            conn = sqlite3.connect("stocks.db")
            historical_data = get_historical_data(conn, ticker)
            if not historical_data.empty:
                open_price = historical_data['open']
                high = historical_data['high']
                low = historical_data['low']
                close = historical_data['close']
                for date, row in historical_data.iterrows():
                    bull_power, bear_power = util.calculate_elder_ray(high, low, close)
                    stock_info = {
                        'price': row['close'],
                        'SMA': util.calculate_sma(historical_data),
                        'EMA': util.calculate_ema(close),
                        'TRIX': util.calculate_trix(close),
                        'AROON_UP': util.calculate_aroon(high, low)[0],
                        'AROON_DOWN': util.calculate_aroon(high, low)[1],
                        'BULL_POWER': bull_power,
                        'BEAR_POWER': bear_power,
                        'HEIKIN_ASHI_CLOSE': util.calculate_heikin_ashi(open_price, high, low, close),
                        'PSAR': util.calculate_parabolic_sar(close, low, high),
                        'RSI': util.calculate_rsi(close),
                        'historical_data': historical_data
                    }
                    signal = strategy(stock_info)
                    if isinstance(signal, str):
                        if signal == 'buy':
                            Backtester.buy_stock(ticker, row['close'], date)
                        elif signal == 'sell':
                            Backtester.sell_stock(ticker, row['close'], date)
                    else:
                        logging.warning(f"Invalid signal for {ticker} on {date}: {signal}")
            else:
                logging.warning(f"No historical data for {ticker}")
        except Exception as e:
            logging.error(f"Error fetching data for {ticker}: {e}")
        finally:
            conn.close()

    def run_strategy_multiprocessing(self, strategy_name, tickers):
        strategy = self.strategies[strategy_name]
        with mp.Pool(processes=mp.cpu_count()) as pool:
            pool.starmap(self.run_strategy, [(strategy, ticker) for ticker in tickers])

    def run_backtest(self, start_date, end_date, initial_balance):
        backtester = Backtester(start_date, end_date, initial_balance)
        conn = sqlite3.connect("stocks.db")
        tickers = get_all_tickers(conn)
        conn.close()

        batches = list(util.partition_array(tickers, 10))  # Split tickers into batches of 10

        total_batches = len(batches)
        total_start_time = time.time()

        for batch_num, batch in enumerate(batches):
            batch_start_time = time.time()
            logging.info(f"Starting backtest for batch {batch_num + 1}/{total_batches}: {batch}")
            print(f"Starting backtest for batch {batch_num + 1}/{total_batches}: {batch}")
            for name in self.strategies.keys():
                try:
                    logging.info(f"Running strategy {name} on batch {batch}")
                    print(f"Starting strategy {name} on batch {batch_num + 1}")
                    self.run_strategy_multiprocessing(name, batch)
                    metrics = backtester.calculate_metrics()
                    logging.info(f"Backtest metrics for {name} in batch {batch_num + 1}: {metrics}")
                    print(f"Finished strategy {name} on batch {batch_num + 1}")

                    self.results.append({
                        'strategy': name,
                        'batch': batch,
                        'metrics': metrics
                    })

                    best_strategy = max(metrics, key=metrics.get)
                    self.scores[best_strategy] += 1
                except Exception as e:
                    logging.error(f"Error running strategy {name} on batch {batch}: {e}")
                    print(f"Error running strategy {name} on batch {batch_num + 1}: {e}")
            batch_end_time = time.time()
            batch_duration = batch_end_time - batch_start_time
            logging.info(f"Completed backtest for batch {batch_num + 1}/{total_batches} in {batch_duration:.2f} seconds")
            print(f"Completed backtest for batch {batch_num + 1}/{total_batches} in {batch_duration:.2f} seconds")

            remaining_batches = total_batches - (batch_num + 1)
            if remaining_batches > 0:
                estimated_remaining_time = (batch_duration * remaining_batches) / 60
                logging.info(f"Estimated remaining time: {estimated_remaining_time:.2f} minutes")
                print(f"Estimated remaining time: {estimated_remaining_time:.2f} minutes")

        total_end_time = time.time()
        total_duration = total_end_time - total_start_time
        logging.info(f"Total backtesting duration: {total_duration:.2f} seconds")
        print(f"Total backtesting duration: {total_duration:.2f} seconds")

        best_overall_strategy = max(self.scores, key=self.scores.get)
        logging.info(f"Best overall strategy: {best_overall_strategy} with score: {self.scores[best_overall_strategy]}")
        print(f"Best overall strategy: {best_overall_strategy} with score: {self.scores[best_overall_strategy]}")
        return backtester.calculate_performance()

    def get_results(self):
        return self.results

if __name__ == "__main__":
    logging.basicConfig(filename='backtester.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    db_credentials = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT")
    }
    db_manager = dbHandler(db_credentials)

    strategy_runner = StrategyRunner()
    start_date = "2022-01-01"
    end_date = "2024-05-31"
    initial_balance = 1000

    profiler = cProfile.Profile()
    profiler.enable()
    
    strategy_runner.run_backtest(start_date=start_date, end_date=end_date, initial_balance=initial_balance)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumtime').print_stats(10)

    try:
        results = strategy_runner.get_results()
        for result in results:
            db_manager.save_result(result)
    except Exception as e:
        logging.error(f"Error saving results: {e}")
        print(f"Error saving results: {e}")

    db_manager.close()