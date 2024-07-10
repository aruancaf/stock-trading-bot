import math
import pandas as pd 

# param history : pd.DataFrame
# Return format: [current_sma, previous_sma]
from typing import List

def calculate_sma(history) -> List[float]:
    summation = 0
    for row in history.iterrows():
        summation += row[1]['Close']
    return [summation/len(history.index), (summation - history.iloc[-2]['Close'])/(len(history.index)-1)]
def calculate_sma(data: pd.DataFrame, period: int = 20):
    sma = data['Close'].rolling(window=period).mean()
    return sma.iloc[-1], sma.iloc[-2]

def calculate_ema(data: pd.DataFrame, period: int = 20):
    ema = data['Close'].ewm(span=period, adjust=False).mean()
    return ema.iloc[-1]

def calculate_previous_ema(data: pd.DataFrame, period: int = 20):
    ema = data['Close'].ewm(span=period, adjust=False).mean()
    return ema.iloc[-2]

def calculate_trix(data: pd.DataFrame, period: int = 15):
    trix = data['Close'].ewm(span=period, adjust=False).mean()
    trix_diff = trix.diff()
    trix_signal = (trix_diff / trix.shift()) * 100
    return trix_signal.iloc[-1], trix_signal.iloc[-2]

def calculate_aroon(data: pd.DataFrame, period: int = 25):
    aroon_up = data['High'].rolling(window=period).apply(lambda x: (x.argmax() + 1) * 100 / period, raw=True)
    aroon_down = data['Low'].rolling(window=period).apply(lambda x: (x.argmin() + 1) * 100 / period, raw=True)
    return aroon_up.iloc[-1], aroon_down.iloc[-1]

def calculate_elder_ray(data: pd.DataFrame):
    bull_power = data['High'] - data['Close'].ewm(span=13, adjust=False).mean()
    bear_power = data['Low'] - data['Close'].ewm(span=13, adjust=False).mean()
    return bull_power.iloc[-1], bear_power.iloc[-1]
# param history : pd.DataFrame
def calculate_ema(history) -> int:
    sma = calculate_sma(history)
    weighted_multiplier = 2 / (len(history.index) + 1)
    return history.iloc[-1]['Close']  * weighted_multiplier + sma[1] * (1 - weighted_multiplier)

def calculate_rsi(data: pd.DataFrame, period: int = 14) -> float:
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_price_drop(data: pd.DataFrame, threshold: float) -> bool:
    return data['Open'].iloc[-1] < (1 - threshold) * data['Close'].iloc[-2]

def calculate_volume_spike(data: pd.DataFrame, spike_threshold: float) -> bool:
    return data['Volume'].iloc[-1] > spike_threshold * data['Volume'].iloc[-2]

def calculate_heikin_ashi(data: pd.DataFrame) -> float:
    heikin_ashi_close = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4
    return heikin_ashi_close.iloc[-1]

def partition_array(array, number_of_partitions):
    partition_size = math.ceil(len(array)/number_of_partitions)
    chunked = []
    for i in range(number_of_partitions):
        if len(array) != 0:
            chunked.append(array[0:partition_size])
            del array[0:partition_size]
    return chunked

def calculate_price_change(final_price:int, original_price:int):
    return (final_price - original_price)/original_price

def check_overlap(phrase, sentence):
    if phrase !=  None and sentence != None:
        phrase_partitioned = phrase.split()

        for phrase in phrase_partitioned:
            for i in range(len(sentence) - 2):
                if len(phrase[i:i+3]) != 3:
                    break
                if phrase[i:i+3] in sentence:
                    return True

    return False

def linear_regress_slope(x_step, y_values):
    try:
        x_mean = (len(y_values)-1)/2
        y_mean = sum(y_values)/len(y_values)
        x_summation_stdev = 0
        y_summation_stdev = 0
        for i in range(0, len(y_values)):
            x_summation_stdev += (i - x_mean)**2
        for i in range(0, len(y_values)):
            y_summation_stdev += (y_values[i] - y_mean)**2

        x_std = (x_summation_stdev/(len(y_values)-1))**0.5
        y_std = (y_summation_stdev/(len(y_values)-1))**0.5

        summation_temp = 0
        for i in range(0, len(y_values)):
            summation_temp += ((i - x_mean)/x_std)*((y_values[i] - y_mean)/y_std)
        correlation_coefficent = summation_temp/(len(y_values) - 1)
        slope = correlation_coefficent * y_std/x_std
        return slope
    except Exception as e:
        return 0
