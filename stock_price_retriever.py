from datetime import date

import yfinance as yf
from pandas_datareader import data as pdr

yf.pdr_override()
import pandas as pd

# Tickers list
# We can add and delete any ticker from the list to get desired ticker live data
ticker_list = ['DJIA', 'DOW', 'LB', 'EXPE', 'PXD', 'MCHP', 'CRM', 'JEC', 'NRG', 'HFC', 'NOW']
today = date.today()

files = []

for ticker in ticker_list:
    print("\n" + ticker + " stock prices\n")
    print(yf.Ticker(ticker).history("1y"))
