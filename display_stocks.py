import matplotlib.pyplot as plt
import stock_data_gatherer as sdg
import stock_analysis
stock_prices = []
n = 90
ticker = "BABA"
for i in range(-n,0,1):
    stock_prices.insert(0, sdg.get_historical_data(ticker, "1d", "1m").iloc[-i].to_dict()['Volume'])
plt.plot(list(range(n)), stock_prices, 'xb-')
# plt.ylim([130, 134])
print("Price Slope: ", sdg.get_price_slope(ticker))
stock_analysis
plt.show()

