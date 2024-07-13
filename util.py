import math
import pandas as pd
import numpy as np
import yfinance as yf
from typing import List, Tuple




def get_historical_data(ticker_symbol: str, time_period: str = '1mo', time_interval: str = '1d') -> pd.DataFrame:
    """
    Fetch historical data for a given ticker symbol.
    
    :param ticker_symbol: The ticker symbol of the stock.
    :param time_period: The period over which to fetch the data (e.g., '1mo', '6mo', '1y').
    :param time_interval: The interval between data points (e.g., '1d', '1wk').
    :return: DataFrame containing historical stock data.
    """
    ticker = yf.Ticker(ticker_symbol)
    return ticker.history(period=time_period, interval=time_interval)
def calculate_rapid_rebound(data: pd.DataFrame, 
                           price_drop_threshold: float = 0.03,
                           volume_spike_threshold: float = 1.5,
                           rsi_period: int = 14,
                           rsi_oversold: int = 30,
                           holding_period: int = 4,
                           profit_target: float = None,
                           stop_loss: float = None) -> Tuple[float, float]:
    
    # Initialize necessary indicators
    data['RSI'] = bt.indicators.RSI(data['Close'], period=rsi_period)
    
    order = None
    entry_price = None
    entry_time = None
    exit_price = None

    # Iterate through each row (assuming data is sorted by date)
    for i in range(1, len(data)):
        if order:
            continue

        # Check for entry conditions
        if (data['Open'][i] < (1 - price_drop_threshold) * data['Close'][i-1] and
            data['Volume'][i] > volume_spike_threshold * data['Volume'][i-1] and
            data['RSI'][i] < rsi_oversold):

            entry_price = data['Close'][i]
            entry_time = data.index[i]
            order = 'BUY'

        # Check for exit conditions
        if order:
            current_time = data.index[i]
            exit_time = entry_time + pd.Timedelta(days=holding_period)

            if (data['Close'][i] >= entry_price * (1 + profit_target) or
                data['Close'][i] <= entry_price * (1 - stop_loss) or
                current_time >= exit_time):
                exit_price = data['Close'][i]
                order = 'SELL'

    return entry_price, exit_price

def calculate_ema(data: pd.DataFrame, period: int = 20) -> float:
    ema = data['Close'].ewm(span=period, adjust=False).mean()
    return ema.iloc[-1]

def calculate_moving_average(data: pd.DataFrame, period: int = 50) -> float:
    sma = data['Close'].rolling(window=period).mean()
    return sma.iloc[-1]

def calculate_volume(data: pd.DataFrame) -> float:
    return data['Volume'].iloc[-1]

def calculate_trix(data: pd.DataFrame, period: int = 15) -> float:
    ema1 = data['Close'].ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    trix = 100 * (ema3.diff() / ema3.shift(1))
    return trix.iloc[-1]

def calculate_aroon(data: pd.DataFrame, period: int = 25) -> Tuple[float, float]:
    aroon_up = data['High'].rolling(window=period).apply(lambda x: (x.argmax() + 1) * 100 / period, raw=True)
    aroon_down = data['Low'].rolling(window=period).apply(lambda x: (x.argmin() + 1) * 100 / period, raw=True)
    return aroon_up.iloc[-1], aroon_down.iloc[-1]

def calculate_elder_ray(data: pd.DataFrame) -> Tuple[float, float]:
    bull_power = data['High'] - data['Close'].ewm(span=13, adjust=False).mean()
    bear_power = data['Low'] - data['Close'].ewm(span=13, adjust=False).mean()
    return bull_power.iloc[-1], bear_power.iloc[-1]

def calculate_heikin_ashi(data: pd.DataFrame) -> float:
    ha_close = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4
    return ha_close.iloc[-1]

def calculate_rsi(data: pd.DataFrame, period: int = 14) -> float:
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_parabolic_sar(data: pd.DataFrame, af_start: float = 0.02, af_increment: float = 0.02, af_max: float = 0.2) -> pd.Series:
    psar = data['Close'].copy()
    psar.iloc[0] = data['Low'].iloc[0]
    uptrend = True
    af = af_start
    ep = data['High'].iloc[0]

    for i in range(1, len(data)):
        if uptrend:
            psar.iloc[i] = psar.iloc[i - 1] + af * (ep - psar.iloc[i - 1])
            if data['Low'].iloc[i] < psar.iloc[i]:
                uptrend = False
                psar.iloc[i] = ep
                ep = data['Low'].iloc[i]
                af = af_start
        else:
            psar.iloc[i] = psar.iloc[i - 1] - af * (psar.iloc[i - 1] - ep)
            if data['High'].iloc[i] > psar.iloc[i]:
                uptrend = True
                psar.iloc[i] = ep
                ep = data['High'].iloc[i]
                af = af_start

        if uptrend:
            if data['High'].iloc[i] > ep:
                ep = data['High'].iloc[i]
                af = min(af + af_increment, af_max)
        else:
            if data['Low'].iloc[i] < ep:
                ep = data['Low'].iloc[i]
                af = min(af + af_increment, af_max)

    return psar

def calculate_sma(data: pd.DataFrame, period: int = 20) -> Tuple[float, float]:
    sma = data['Close'].rolling(window=period).mean()
    return sma.iloc[-1], sma.iloc[-2]

def calculate_trix_signal(data: pd.DataFrame, period: int = 15) -> Tuple[float, float]:
    trix = data['Close'].ewm(span=period, adjust=False).mean()
    trix_diff = trix.diff()
    trix_signal = (trix_diff / trix.shift()) * 100
    return trix_signal.iloc[-1], trix_signal.iloc[-2]

def calculate_price_drop(data: pd.DataFrame, threshold: float) -> bool:
    return data['Open'].iloc[-1] < (1 - threshold) * data['Close'].iloc[-2]

def calculate_volume_spike(data: pd.DataFrame, spike_threshold: float) -> bool:
    return data['Volume'].iloc[-1] > spike_threshold * data['Volume'].iloc[-2]

def calculate_volume_slope(data: pd.DataFrame) -> float:
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Expected data to be a pandas DataFrame")

    if 'Volume' not in data.columns:
        raise ValueError("DataFrame must contain 'Volume' column")

    volumes = data['Volume']
    x = np.arange(len(volumes))  # Time points
    y = volumes.values
    
    # Perform linear regression
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]
    
    return m

def get_volume_slope(ticker_symbol: str, historical_data: pd.DataFrame) -> float:
    return calculate_volume_slope(historical_data)

def partition_array(array, number_of_partitions):
    partition_size = math.ceil(len(array) / number_of_partitions)
    chunked = []
    for _ in range(number_of_partitions):
        if len(array) != 0:
            chunked.append(array[:partition_size])
            del array[:partition_size]
    return chunked

def calculate_price_change(final_price: int, original_price: int) -> float:
    return (final_price - original_price) / original_price

def check_overlap(phrase: str, sentence: str) -> bool:
    if phrase is not None and sentence is not None:
        phrase_partitioned = phrase.split()
        for phrase in phrase_partitioned:
            for i in range(len(sentence) - 2):
                if len(phrase[i:i + 3]) != 3:
                    break
                if phrase[i:i + 3] in sentence:
                    return True
    return False

def linear_regress_slope(x_step, y_values):
    try:
        x_mean = (len(y_values)-1)/2
        y_mean = sum(y_values)/len(y_values)
        x_summation_stdev = sum((I - x_mean)**2 for I in range(len(y_values)))
        y_summation_stdev = sum((y - y_mean) ** 2 for y in y_values)
        x_std = (x_summation_stdev/(len(y_values)-1))**0.5
        y_std = (y_summation_stdev/(len(y_values)-1))**0.5

        summation_temp = sum(
            ((I - x_mean) / x_std) * ((y_values.iloc[I] - y_mean) / y_std)
            for I in range(len(y_values))
        )
        correlation_coefficent = summation_temp/(len(y_values) - 1)
        return correlation_coefficent * y_std/x_std
    except Exception as e:
        return 0