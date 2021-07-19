import numpy as np


class TrainingInput:
    @staticmethod
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

    def __init__(
            self,
            high_price: float,
            low_price: float,
            timeseries_price,
            high_volume: float,
            low_volume: float,
            timeseries_volume):

        # first 30 elements are historical data points w/ 1 min incr; next 10
        # min are used for prediction
        assert len(timeseries_price) == 40 and len(timeseries_volume) == 40

        self.timeseries_price = timeseries_price
        self.timeseries_volume = timeseries_volume

        # print("Initializing Input")
        price_summation = high_price + low_price + \
            sum(timeseries_price[-40:-10])
        price_mean = price_summation / (len(timeseries_price[-40:-10]) + 2)
        price_std = np.std(timeseries_price[-40:-10] + [high_price, low_price])

        volume_summation = sum(timeseries_volume[-40:-10])
        volume_mean = (volume_summation / len(timeseries_volume[-40:-10]))
        volume_std = np.std(timeseries_volume[-40:-10])

        if price_std == 0:
            price_std = 1
        if volume_std == 0:
            volume_std = 1

        # Normalized price and volume

        self.high_price = (high_price - price_mean) / price_std
        self.low_price = (low_price - price_mean) / price_std
        self.high_volume = (high_volume - volume_mean) / volume_std
        self.low_volume = (low_volume - volume_mean) / volume_std

        # normalizes price (z-score)
        timeseries_price_normalized = [(price - price_mean) /
                                       price_std for price in timeseries_price]

        self.timeseries_price_x = timeseries_price_normalized[-40:-10]
        self.timeseries_price_slope_y = TrainingInput.linear_regression_slope(
            timeseries_price_normalized[-10:])
        self.timeseries_volume_x = [
            (volume -
             volume_mean) /
            volume_std for volume in timeseries_volume[-40:-10]]  # normalizes volume (z-score)

    def get_serialized_input(self):
        input_state = np.zeros((4, 30,))
        input_state[0] = np.array(self.timeseries_price_x)
        # input_state[1] = np.concatenate(
            # (np.array([self.low_price, self.high_price]), np.zeros(28)))
        # input_state[2] = np.array(self.timeseries_volume_x)
        # input_state[3] = np.concatenate(
            # (np.array([self.low_volume, self.high_volume]), np.zeros(28)))

        return input_state

    '''
    [1, 0, 0] if should buy
    [0, 1, 0] if neutral
    [0, 0, 1] if should sell
    '''

    def get_serialized_output(self):
        # print("Slope: ", self.timeseries_price_slope_y)
        return [1, 0, 0] if self.timeseries_price_slope_y > 0.008 else (
            [0, 1, 0] if self.timeseries_price_slope_y > -0.008 else [0, 0, 1])

    def get_original_timeseries_price(self):
        return self.timeseries_price

    def get_original_timeseries_volume(self):
        return self.timeseries_volume

    @staticmethod
    def map(output):
        return {
            "[1, 0, 0]": "buy",
            "[0, 1, 0]": "neutral",
            "[0, 0, 1]": "sell"}[
            str(output)]
