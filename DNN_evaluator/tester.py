import numpy as np
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


a = [1, 2, 3, 4, 5]

assert linear_regression_slope(a) == LinearRegression().fit(np.array(range(0, 5)).reshape((-1, 1)),a).coef_
