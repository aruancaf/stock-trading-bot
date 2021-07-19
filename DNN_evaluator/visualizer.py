import tensorflow as tf
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


dataset = np.load("timeseries_test_dataset.npz")
model = tf.keras.models.load_model("trading_modelV0.h5")
for i in range(0, 100):
    fig, axs = plt.subplots(2, 1)
    fig.set_size_inches((8, 8))
    # print(dataset['x'][0][0])

    axs[0].plot(range(30), dataset['x'][i][0])
    axs[0].set_xlabel('Time (min)')
    axs[0].set_ylabel('Normalized Price')

    axs[0].grid(True)
    slope = linear_regression_slope(dataset['x'][i][0])
    print("Prediction: ", TrainingInput.map(model.predict(TrainingInput(False, 0, 0, dataset['x'][i][0], 0, 0, [0]*30).get_serialized_input()), False))
    print("GroundTruth: ",  TrainingInput.map(dataset['y'][i].tolist(), True)) # doesn't match up since dataset['y'] is for future label and dataset['x'] is model input
    axs[0].plot(range(30), [slope * i for i in range(30)])
    fig.tight_layout()
    # plt.show(block=False)
    # time.sleep(5)
    plt.show()
