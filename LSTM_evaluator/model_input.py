import numpy as np

class TrainingInput:

    def __init__(self, high_price, low_price, timeseries_price, high_volume, low_volume, timeseries_volume):
        print("Initializing Input")
        self.high_price = high_price
        self.low_price = low_price
        self.high_volume = high_volume
        self.low_volume = low_volume
        price_summation = self.high_price + self.low_price + sum(timeseries_price[-15:-1])
        price_mean = price_summation / (len(timeseries_price[-15:-1]) + 2)
        price_std = np.std(timeseries_price[-15:-1] + [high_price, low_price])

        volume_summation = sum(timeseries_volume)
        volume_mean = (volume_summation / len(timeseries_volume))
        volume_std = np.std(timeseries_volume)

        timeseries_price = [(price - price_mean)/price_std for price in timeseries_price] # normalizes price (z-score)
        self.timeseries_price_x = timeseries_price[-30:-15]
        self.timeseries_price_y = timeseries_price[-15:]
        self.timeseries_volume = [(volume - volume_mean)/volume_std for volume in timeseries_volume] # normalizes volume (z-score)


    def get_serialized_input(self):
        print("Serialized Output")
    def get_output(self):
        print(self.timeseries_price_y)
        # return [1, 0, 0] if should_buy else ([0, 1, 0] if neutral else [0, 0, 1])# TODO: should not just predict next price in 1 min. Should predict slope of price few minutes later
        return self.timeseries_price_y
