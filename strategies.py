import pandas as pd
import numpy as np

# strategies.py
def strategySmaCrossover(market, period, stratParams=None):
    if stratParams is None:
        stratParams = [5, 10]
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
def meanReversionStrategy(market, period, stratParams=None):
    if stratParams is None:
        stratParams = {
            'window': 20,
            'threshold': 2,
            'ma_type': 'sma',  # 'sma' for simple moving average, 'ema' for exponential moving average
            'stop_loss': 0.05,  # 5% stop-loss
            'take_profit': 0.4  # 40% take-profit
        }
    
    window = stratParams['window']
    threshold = stratParams['threshold']
    ma_type = stratParams['ma_type']
    stop_loss = stratParams['stop_loss']
    take_profit = stratParams['take_profit']

    if period < window:
        return 'no position'

    if ma_type == 'sma':
        moving_average = market.sma(period, window)
    elif ma_type == 'ema':
        moving_average = market.data.iloc[:period+1].ewm(span=window, adjust=False).mean().iloc[-1]

    price = market.data.iloc[period]

    # Buy signal: price is significantly below the moving average
    if price < moving_average - threshold:
        return 'buy'
    
    # Sell signal: price is significantly above the moving average
    elif price > moving_average + threshold:
        return 'sell'
    
    # Stop-loss and take-profit levels
    if market.data.iloc[period - 1] * (1 - stop_loss) >= price:
        return 'sell'  # Stop-loss triggered
    if market.data.iloc[period - 1] * (1 + take_profit) <= price:
        return 'sell'  # Take-profit triggered
    
    return 'hold'