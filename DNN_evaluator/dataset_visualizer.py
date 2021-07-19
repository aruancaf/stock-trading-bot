import numpy as np
import matplotlib.pyplot as plt
# from matplotlib.pyplot import figure
import time
from training_input import TrainingInput
from sklearn.linear_model import LinearRegression

# assumes x values have step of 1


def linear_regression_slope(y_values):
    x_mean = (len(y_values) - 1) / 2
    y_mean = sum(y_values) / len(y_values)
    x_summation_stdev = 0
    y_summation_stdev = 0
    for i in range(0, len(y_values)):
        x_summation_stdev += (i - x_mean)**2
    for i in range(0, len(y_values)):
        y_summation_stdev += (y_values[i] - y_mean)**2

    x_std = (x_summation_stdev / (len(y_values) - 1))**0.5
    y_std = (y_summation_stdev / (len(y_values) - 1))**0.5

    if y_std == 0:
        return 0

    summation_temp = 0
    for i in range(0, len(y_values)):
        summation_temp += ((i - x_mean) / x_std) * \
            ((y_values[i] - y_mean) / y_std)
    correlation_coefficent = summation_temp / (len(y_values) - 1)
    slope = correlation_coefficent * y_std / x_std
    return slope


dataset = np.load("timeseries_dataset.npz")
for i in range(0, 100):
    fig, axs = plt.subplots(2, 1)
    fig.set_size_inches((8, 8))
    # print(dataset['x'][0][0])

    axs[0].plot(range(30), dataset['x'][i][0])
    # axs[0].plot(range(30), [dataset['x'][0][1][0]] * 30)
    # axs[0].plot(range(30), [dataset['x'][0][1][1]] * 30)
    axs[0].set_xlabel('Time (min)')
    axs[0].set_ylabel('Normalized Price')

    axs[0].grid(True)
    slope = linear_regression_slope(dataset['x'][i][0])
    print(TrainingInput.map(dataset['y'][i].tolist()) + " Slope: %0.5f" % slope, end='\r') # doesn't match up since dataset['y'] is for future label and dataset['x'] is model input
    # print(
    #     "Slope: %0.5f" %
    #     LinearRegression().fit(
    #         np.array(
    #             range(
    #                 0, 30)).reshape(
    #             (-1, 1)), dataset['x'][i][0]).coef_)
    
    axs[0].plot(range(30), [slope * i for i in range(30)])
    fig.tight_layout()
    # plt.show(block=False)
    # time.sleep(5)
    plt.show()
