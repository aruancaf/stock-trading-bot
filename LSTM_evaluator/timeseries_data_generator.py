import yfinance as yf
import pandas as pd
import time
import pandas as pd
from datetime import datetime, date
import os 


stocks = []
with open("stocks_to_download.txt", "r") as f:
    stocks = [i.replace("\n", "") for i in f.readlines()]

print(stocks)
download_path = "timeseries_data/"
for file in os.listdir(download_path):
    os.remove(os.path.join(download_path, file))


f = open("time_series_stock_data.txt", "a")
for stock in stocks:
    start_date = "2021-06-16" # starts downloading data starting from this date
    end_date = "2021-07-15"
    download_interval = pd.date_range(start=start_date,end=end_date)[::7] # only allows download for 7 day intervals

    for i in range(0, len(download_interval) - 1):
        print(stock)

        data = yf.download(
            tickers = stock,
            # use "period" instead of start/end
            # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            # (optional, default is '1mo')
            period = "7d",

            # fetch data by interval (including intraday if period < 60 days)
            # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            # (optional, default is '1d')
            interval = "1m",

            start=download_interval[i],
            end=download_interval[i+1],

            # download pre/post regular market hours data
            # (optional, default is False)
            prepost = False,


            # use threads for mass downloading? (True/False/Integer)
            # (optional, default is True)
            threads = True,
        )

        data_file_path = "timeseries_data/%s.csv"
        with open(data_file_path, 'a') as f:
            data.to_csv("timeseries_data/%s.csv" % stock, header=f.tell()==0)


f.close()
