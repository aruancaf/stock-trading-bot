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
                        'SMA': util.calculate_sma(historical_data)[0],
                        'PREVPRICE': row['Close'],
                        'PREVSMA': util.calculate_sma(historical_data)[1],
                        'TRIX': util.calculate_trix(historical_data)[0],
                        'PREVTRIX': util.calculate_trix(historical_data)[1],
                        'AROON_UP': util.calculate_aroon(historical_data)[0],
                        'AROON_DOWN': util.calculate_aroon(historical_data)[1],
                        'BULL_POWER': util.calculate_elder_ray(historical_data)[0],
                        'BEAR_POWER': util.calculate_elder_ray(historical_data)[1],
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
        df = pd.DataFrame(self.trades)
        if 'price' not in df.columns:
            raise KeyError("The 'price' column is missing in the trades DataFrame.")
        if 'date' not in df.columns:
            raise KeyError("The 'date' column is missing in the trades DataFrame.")
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
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
        elif current_win_streak > 0:
            win_streaks.append(current_win_streak)
        if current_loss_streak > 0:
            loss_streaks.append(current_loss_streak)

        return win_streaks, loss_streaks

class StrategyRunner:
    def __init__(self):
        self.strategies = {
            "combined_strategy": self.combined_strategy,
            # Add other strategies if needed
        }

    def combined_strategy(self, ticker, stock_info) -> float:
        score = 0
        score += util.moving_average_checker(ticker, stock_info)
        score += util.volume_checker(ticker, stock_info)
        score += util.trix_checker(ticker, stock_info)
        score += util.aroon_checker(ticker, stock_info)
        score += util.elder_ray_checker(ticker, stock_info)
        score += util.heikin_ashi_checker(ticker, stock_info)
        score += util.rapid_rebound_checker(ticker, stock_info)
        score += util.parabolic_sar_checker(ticker, stock_info)
        return score

    def run_backtest(self, start_date, end_date, initial_balance):
        backtester = Backtester(start_date, end_date, initial_balance)
        tickers = scraper.active_stocks() + const.STOCKS_TO_CHECK  # Pull the symbols from the scraper module and constants file
        batches = util.partition_array(tickers, 10)  # Split tickers into batches of 10
        for batch_num, batch in enumerate(batches):
            logging.info(f"Starting backtest for batch {batch_num + 1}/{len(batches)}: {batch}")
            for name, strategy in self.strategies.items():
                backtester.run_strategy(strategy, batch)
                final_balance = backtester.calculate_performance()
                logging.info(f"Final balance for {name} in batch {batch_num + 1}: {final_balance}")
                logging.info(f"Trades executed in batch {batch_num + 1}: {backtester.trades}")
                metrics = backtester.calculate_metrics()
                logging.info(f"Backtest metrics for {name} in batch {batch_num + 1}: {metrics}")
            logging.info(f"Completed backtest for batch {batch_num + 1}/{len(batches)}")
            
class StrategyRunner:
    def __init__(self):
        self.strategies = {
            "combined_strategy": sa.combined_strategy,
            "moving_average_strategy": sa.moving_average_checker,
            "volume_strategy": sa.volume_checker,
            "trix_strategy": sa.trix_checker,
            "aroon_strategy": sa.aroon_checker,
            "elder_ray_strategy": sa.elder_ray_checker,
            "heikin_ashi_strategy": sa.heikin_ashi_checker,
            "rapid_rebound_strategy": sa.rapid_rebound_checker,
            "parabolic_sar_strategy": sa.parabolic_sar_checker,
        }

    def run_backtest(self, start_date, end_date, initial_balance):
        backtester = bt.Backtester(start_date, end_date, initial_balance)
        tickers = scraper.active_stocks() + const.STOCKS_TO_CHECK  # Pull the symbols from the scraper module and constants file
        batches = util.partition_array(tickers, 10)  # Split tickers into batches of 10
        strategy_metrics = {}

        for batch_num, batch in enumerate(batches):
            logging.info(f"Starting backtest for batch {batch_num + 1}/{len(batches)}: {batch}")
            for name, strategy in self.strategies.items():
                backtester.run_strategy(strategy, batch)
                final_balance = backtester.calculate_performance()
                logging.info(f"Final balance for {name} in batch {batch_num + 1}: {final_balance}")
                logging.info(f"Trades executed in batch {batch_num + 1}: {backtester.trades}")
                metrics = backtester.calculate_metrics()
                logging.info(f"Backtest metrics for {name} in batch {batch_num + 1}: {metrics}")
                if name not in strategy_metrics:
                    strategy_metrics[name] = metrics
                else:
                    # Combine metrics from different batches
                    strategy_metrics[name] = self._combine_metrics(strategy_metrics[name], metrics)
            logging.info(f"Completed backtest for batch {batch_num + 1}/{len(batches)}")

        logging.info("Completed backtest")
        return strategy_metrics

    def _combine_metrics(self, metrics1, metrics2):
        combined_metrics = {}
        for key in metrics1:
            if isinstance(metrics1[key], (int, float)):
                combined_metrics[key] = metrics1[key] + metrics2[key]
            elif isinstance(metrics1[key], list):
                combined_metrics[key] = metrics1[key] + metrics2[key]
        return combined_metrics

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(filename='backtester.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # Running Backtests
    strategy_runner = StrategyRunner()
    strategy_runner.run_backtest(start_date="2019-01-01", end_date="2023-12-31", initial_balance=1000)
    # Remove the reference to strategy_metrics)