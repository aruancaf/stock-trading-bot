import math
import pandas

# param history : pd.DataFrame
# Return format: [current_sma, previous_sma]
def calculate_sma(history) -> []:
    summation = 0
    for row in history.iterrows():
        summation += row[1]['Close']
    return [summation/len(history.index), (summation - history.iloc[0]['Close'])/len(history.index)]


# param history : pd.DataFrame
def calculate_ema(history) -> int:
    sma = calculate_sma(history)
    weighted_multiplier = 2 / (len(history.index) + 1)
    return history.iloc[0]['Close']  * weighted_multiplier + sma[1] * (1 - weighted_multiplier)
