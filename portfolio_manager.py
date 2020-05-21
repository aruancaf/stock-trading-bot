import yfinance as yf

from utils import json_simplifier


class PortfolioManager:
    stocks = {}

    def get_position_polarity(self) -> float:
        position_polarity = 0
        json_simplifier.readJson('stock_portfolio.json')
        for i in self.stocks:
            print("{0} {1}".format(i, yf.Ticker(i).history("1d").iloc[0]['Close'] - self.stocks[i]['Close']))
            position_polarity += yf.Ticker(i).history("1d").iloc[0]['Close'] - self.stocks[i]['Close']
        return position_polarity
