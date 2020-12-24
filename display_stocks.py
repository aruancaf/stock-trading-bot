import matplotlib.pyplot as plt
import stock_data_gatherer as sdg
stock_prices = []
for i in range(-5, 0):
    stock_prices.append(sdg.get_historical_data("AAPL", "1d", "1m").iloc[-i].to_dict()['Close'])
plt.scatter([0, 1, 2, 3, 4], stock_prices)
plt.show()

