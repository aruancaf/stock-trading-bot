import yfinance as yf

msft = yf.Ticker("AAPL")

# get stock info
print(msft.history("1d").iloc[0])
