import matplotlib.pyplot as plt
import stock_data_gatherer as sdg
import stock_analysis
stock_prices = []
n = 180
ticker = "AAPL"
for i in range(-n,0,1):
    stock_prices.append(sdg.get_historical_data(ticker, "1d", "1m").iloc[i].to_dict()['Volume'])
plt.plot(list(range(n)), stock_prices, 'xb-')
# plt.ylim([130, 134])

print("Price Slope: ", sdg.get_volume_slope(ticker)/(0.2*sdg.get_current_stock_data(ticker)['Volume']))
plt.show()

