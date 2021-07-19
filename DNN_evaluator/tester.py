import numpy as np
from sklearn.linear_model import LinearRegression
import yfinance as yf


data = yf.download(
tickers='AAPL',
# use "period" instead of start/end
# valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
# (optional, default is '1mo')
period="7d",

# fetch data by interval (including intraday if period < 60 days)
# valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
# (optional, default is '1d')
interval="1m",

# download pre/post regular market hours data
# (optional, default is False)
prepost=True,


# use threads for mass downloading? (True/False/Integer)
# (optional, default is True)
threads=True,
)

time = data.index.values
for a in time:
    print(str(a).split('T')[0])
# # assumes x values have step of 1
#
#
# def linear_regression_slope(y_values):
#     x_mean = (len(y_values) - 1) / 2
#     y_mean = sum(y_values) / len(y_values)
#     x_summation_stdev = 0
#     y_summation_stdev = 0
#     for i in range(0, len(y_values)):
#         x_summation_stdev += (i - x_mean)**2
#         for i in range(0, len(y_values)):
#             y_summation_stdev += (y_values[i] - y_mean)**2
#
#             x_std = (x_summation_stdev / (len(y_values) - 1))**0.5
#             y_std = (y_summation_stdev / (len(y_values) - 1))**0.5
#
#             if y_std == 0:
#                 return 0
#
#             summation_temp = 0
#             for i in range(0, len(y_values)):
#                 summation_temp += ((i - x_mean) / x_std) * \
#                     ((y_values[i] - y_mean) / y_std)
#                 correlation_coefficent = summation_temp / (len(y_values) - 1)
#                 slope = correlation_coefficent * y_std / x_std
#                 return slope
#
#
# a = [1, 2, 3, 4, 5]
#
# assert linear_regression_slope(a) == LinearRegression().fit(
#     np.array(range(0, 5)).reshape((-1, 1)), a).coef_
