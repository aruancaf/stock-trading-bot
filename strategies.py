import pandas as pd
import numpy as np


#strategies.py
def strategySmaCrossover(market, period, stratParams=[5,10]):
    fastSMA = stratParams[0]
    slowSMA = stratParams[1]
    if market.sma(period - 2, slowSMA) == 0:
        return 'no position'
    if market.sma(period - 1, fastSMA) < market.sma(period - 1, slowSMA):  # downtrend
        if market.sma(period, fastSMA) > market.sma(period, slowSMA):  # downtrend reversal
            return "closelong"
        else:
            return 'no posittion'

    elif market.sma(period - 1, fastSMA) > market.sma(period - 1, slowSMA):  # uptrend
        if market.sma(period, fastSMA) < market.sma(period, slowSMA):  # uptrend reversal
            return "closeshort"
        else:
            return 'no posittion'
    else:
        return 'no posittion'


def meanReversionStrategy(market, period, stratParams=[20, 2]):
    window = stratParams[0]
    threshold = stratParams[1]
    
    if period < window:
        return 'no position'
    
    moving_average = market.sma(period, window)
    price = market.data[period]
    
    if price < moving_average - threshold:  # Price is significantly below the moving average
        return 'buy'
    elif price > moving_average + threshold:  # Price is significantly above the moving average
        return 'sell'
    else:
        return 'hold'