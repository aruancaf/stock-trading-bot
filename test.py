import stock_analysis
import scraper
import stock_data_gatherer
import math

stocks = scraper.active_stocks()

print(len(stocks))

x = 5 # number of partitions

number_of_stocks = len(stocks)


stocks_per_partition = math.floor(number_of_stocks/x)


print("stocks per partition", stocks_per_partition)

chunked_stocks = []

for i in range(x):
    print(stocks[0:stocks_per_partition])
    chunked_stocks.append(stocks[0:number_of_stocks])
    del stocks[0:stocks_per_partition]
    
for x in chunked_stocks:
    print(x)
    print("\n\n\n\n")





