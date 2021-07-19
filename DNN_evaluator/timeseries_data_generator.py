import yfinance as yf
import pandas as pd
import time
import pandas as pd
from datetime import datetime, date, timedelta
import os
from training_input import TrainingInput
import random
import numpy as np
import contextlib
import matplotlib.pyplot as plt


wants_visualization = False
# https://towardsdatascience.com/lstm-for-time-series-prediction-de8aeb26f2ca
stocks = []
with open("stocks_to_download.txt", "r") as f:
    stocks = [i.replace("\n", "") for i in f.readlines()]

download_path = "raw_timeseries_data/"
for file in os.listdir(download_path):
    os.remove(os.path.join(download_path, file))

final_model_input = []
# starts downloading data starting from this date
start_date = date.today() - timedelta(days=29)
end_date = date.today()
counter = 0

print("Downloading from %s to %s" % (start_date, end_date))

for stock in stocks:
    download_interval = pd.date_range(start=start_date, end=end_date)[
        ::7]  # only allows download for 7 day intervals
    for i in range(0, len(download_interval) - 1):
        with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
            data = yf.download(
                tickers=stock,
                # use "period" instead of start/end
                # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                # (optional, default is '1mo')
                period="7d",

                # fetch data by interval (including intraday if period < 60 days)
                # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                # (optional, default is '1d')
                interval="1m",

                start=download_interval[i],
                end=download_interval[i + 1],

                # download pre/post regular market hours data
                # (optional, default is False)
                prepost=True,


                # use threads for mass downloading? (True/False/Integer)
                # (optional, default is True)
                threads=True,
            )

        data_file_path = os.path.join(download_path, "%s.csv" % stock)
        with open(data_file_path, 'a') as f:
            data.to_csv(data_file_path, header=f.tell() == 0)

        timeseries_length = 40
        close_prices_7_day = data['Close'].to_numpy()
        volume_7_day = data['Volume'].to_numpy()
        price_dates = [str(i).split('T')[0] for i in data.index.values]
        counter += len(data['Close'].to_list())

        # if len(close_prices_7_day) == 0:
        #     print("Found no data", stock)
        #     print(data.head())
        #     exit(0)

        max_price_7_day = max(close_prices_7_day)
        min_price_7_day = min(close_prices_7_day)

        max_volume_7_day = max(volume_7_day)
        min_volume_7_day = min(volume_7_day)

        # print("\n%s\nMax: %s Min: %s\n\n" % (stock, str(max_price_7_day), str(min_price_7_day)))
        for i in range(0, len(close_prices_7_day) - timeseries_length):
            if price_dates[i] == price_dates[i + timeseries_length]: # capture x min timeseries windows from same day to prevent capturing interday news-based morning price swings
                final_model_input.append(TrainingInput(True,
                                                       max_price_7_day,
                                                       min_price_7_day,
                                                       close_prices_7_day[i:i + timeseries_length].tolist(),
                                                       max_volume_7_day,
                                                       min_volume_7_day,
                                                       volume_7_day[i:i + timeseries_length].tolist()))

        # print("2 Week Dataset Size:", len(model_input))
        print("Cumulative Dataset Size:", len(final_model_input), end='\r')

print("Cumulative Dataset Size before balancing", len(final_model_input))
print("Counter:", counter)

# shuffle input

random.shuffle(final_model_input)

# balance input

input_buy = []
input_neutral = []
input_sell = []
test_input = [] # stores rest of samples which are removed for balancing

for inputl in final_model_input:
    input_buysellneutral = TrainingInput.map(inputl.get_serialized_output(), True)
    if input_buysellneutral == "buy":
        input_buy.append(inputl)
    elif input_buysellneutral == "neutral":
        input_neutral.append(inputl)
    else:
        input_sell.append(inputl)

print("Category Breakdown - Buy Window Quantity: %f, Sell Window Quantity: %f, Neutral Window Quantity: %f" % (len(input_buy), len(input_sell), len(input_neutral)))

# most number of buy sell and neutral classifications in training set allowed
class_max = min(len(input_buy), len(input_neutral), len(input_sell))
while len(input_buy) > class_max:
    test_input.append(input_buy.pop())
while len(input_sell) > class_max:
    test_input.append(input_sell.pop())
while len(input_neutral) > class_max:
    test_input.append(input_neutral.pop())

assert len(input_buy) == len(input_sell) == len(input_neutral)  # asserts balanced

final_model_input = input_buy + input_sell + input_neutral

# shuffle input after balance

random.shuffle(final_model_input)
random.shuffle(test_input)


print("Training Dataset Size", len(final_model_input))


# unpack into x and y training data

dataset_x, dataset_y = [], []
test_dataset_x, test_dataset_y = [], []

for i in range(0, len(final_model_input)):
    dataset_x.append(final_model_input[i].get_serialized_input())
    dataset_y.append(final_model_input[i].get_serialized_output())
    if wants_visualization: # TODO: Finish or even needed?
        # Visualization
        fig, axs = plt.subplots(2, 1)
        fig.set_size_inches((8, 8))

        axs[0].plot(range(30), dataset_x[i][0])
        axs[0].set_xlabel('Time (min)')
        axs[0].set_ylabel('Normalized Price')

        axs[0].grid(True)
        slope = TrainingInput.linear_regression_slope(dataset_x[i][0])
        print(TrainingInput.map(dataset_y[i].tolist(), True) + " Slope: %0.5f" % slope, end='\r')
        axs[0].plot(range(30), [slope * i for i in range(30)])
        fig.tight_layout()
        # plt.show(block=False)
        # time.sleep(5)
        plt.show()

for i in range(0, len(test_input)):
    test_dataset_x.append(test_input[i].get_serialized_input())
    test_dataset_y.append(test_input[i].get_serialized_output())

save_status = input("Would you like to save? yes or no: ")
if save_status == "yes":
    np.savez(
        "timeseries_dataset",
        x=np.array(dataset_x),
        y=np.array(dataset_y))
    np.savez(
        "timeseries_test_dataset",
        x=np.array(test_dataset_x),
        y=np.array(test_dataset_y))
