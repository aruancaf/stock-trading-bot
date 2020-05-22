import yfinance as yf

from utils import json_simplifier


class PortfolioManager:
    stocks = {"Purchased": {}, "Sold": {}}

    def get_position_polarity(self) -> float:
        position_polarity = 0
        json_simplifier.readJson('stock_portfolio.json')
        for i in self.stocks['Purchased']:
            polarity_stock = yf.Ticker(i).history("1d").iloc[0]['Close'] - self.stocks['Purchased'][i]['Close']
            print(
                "{0} {1}".format(i, polarity_stock))
            position_polarity += polarity_stock
            if polarity_stock < 0:
                json_simplifier.sellStock(i)
        return position_polarity
