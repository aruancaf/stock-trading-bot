import numpy as np

class TrainingInput:

    # assumes x values have step of 1
    def __linear_regression_slope(self, y_values):
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

        self.timeseries_price = timeseries_price
        self.timeseries_volume = timeseries_volume

        # print("Initializing Input")
        price_summation = high_price + low_price + \
            sum(timeseries_price[-30:-15])
        price_mean = price_summation / (len(timeseries_price[-30:-15]) + 2)
        price_std = np.std(timeseries_price[-15:-1] + [high_price, low_price])

        volume_summation = sum(timeseries_volume)
        volume_mean = (volume_summation / len(timeseries_volume))
        volume_std = np.std(timeseries_volume)

        # Normalized price and volume
        self.high_price = (high_price - price_mean) / price_std
        self.low_price = (low_price - price_mean) / price_std
        self.high_volume = (high_volume - volume_mean) / volume_std
        self.low_volume = (low_volume - volume_mean) / volume_std

        # normalizes price (z-score)
        timeseries_price_normalized = [(price - price_mean) /
                            price_std for price in timeseries_price]
        self.timeseries_price_x = timeseries_price_normalized[-30:-15]
        self.timeseries_price_slope_y = self.__linear_regression_slope(
            timeseries_price_normalized[-15:])
        self.timeseries_volume_x = [
            (volume -
             volume_mean) /
            volume_std for volume in timeseries_volume]  # normalizes volume (z-score)

    def get_serialized_input(self):
        return np.array([self.timeseries_price_x,
                         [self.low_price,
                          self.high_price],
                         self.timeseries_volume_x,
                         [self.low_volume,
                          self.high_volume]])

    '''
    [1, 0, 0] if should buy
    [0, 1, 0] if neutral
    [0, 0, 1] if should sell
    '''
    def get_serialized_output(self):
        # print("Slope: ", self.timeseries_price_slope_y)
        return [1, 0, 0] if self.timeseries_price_slope_y > 0.005 else ([0, 1, 0] if self.timeseries_price_slope_y > -0.005 else [0, 0, 1])

    def get_original_timeseries_price(self):
        return self.timeseries_price

    def get_original_timeseries_volume(self):
        return self.timeseries_volume

    @staticmethod
    def map(output):
        return {"[1, 0, 0]": "buy", "[0, 1, 0]": "neutral", "[0, 0, 1]": "sell"}[str(output)]


