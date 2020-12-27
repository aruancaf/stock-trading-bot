import math
import pandas

# param history : pd.DataFrame
# Return format: [current_sma, previous_sma]
def calculate_sma(history) -> []:
    summation = 0
    for row in history.iterrows():
        summation += row[1]['Close']
    return [summation/len(history.index), (summation - history.iloc[-2]['Close'])/(len(history.index)-1)]

# param history : pd.DataFrame
def calculate_ema(history) -> int:
    sma = calculate_sma(history)
    weighted_multiplier = 2 / (len(history.index) + 1)
    return history.iloc[-1]['Close']  * weighted_multiplier + sma[1] * (1 - weighted_multiplier)

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
