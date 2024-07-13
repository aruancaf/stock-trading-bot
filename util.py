import math
import pandas as pd
import numpy as np
import yfinance as yf
from typing import List, Optional, Tuple

def partition_array(array, batch_size):
    """
    Partition an array into smaller sublists of a specified size.

    Args:
        array (list): The list to be partitioned.
        batch_size (int): The size of each partition.

    Returns:
        list of lists: A list containing the partitions of the original array.
    """
    for i in range(0, len(array), batch_size):
        yield array[i:i + batch_size]

def calculate_rapid_rebound(data: pd.DataFrame, period: int = 14) -> float:
    """
    Calculate the Rapid Rebound indicator, which measures the percentage increase
    in price over a specified period after a significant drop.
    
    Args:
        data (pd.DataFrame): The stock data with at least a 'close' column.
        period (int): The period over which to calculate the rebound.
    
    Returns:
        float: The percentage increase in price indicating a rapid rebound.
    """
    if 'close' not in data.columns:
        raise ValueError("The data must contain a 'close' column.")

    if len(data) < period:
        raise ValueError(f"The data must contain at least {period} rows.")

    # Calculate the maximum drawdown over the period
    max_price = data['close'].rolling(window=period).max()
    min_price = data['close'].rolling(window=period).min()
    max_drawdown = (min_price - max_price) / max_price

    # Calculate the rebound from the minimum price over the period
    rebound = (data['close'] - min_price) / min_price

    return rebound.iloc[-1] * 100

def calculate_volume(data: pd.DataFrame, period: int = 20) -> float:
    """
    Calculate the average trading volume over a specified period.
    
    Args:
        data (pd.DataFrame): The stock data with at least a 'volume' column.
        period (int): The period over which to calculate the average volume.
    
    Returns:
        float: The average trading volume over the specified period.
    """
    if 'volume' not in data.columns:
        raise ValueError("The data must contain a 'volume' column.")

    if len(data) < period:
        raise ValueError(f"The data must contain at least {period} rows.")

    return data['volume'].rolling(window=period).mean().iloc[-1]


def calculate_sma(data: pd.DataFrame, period: int = 14) -> Tuple[Optional[float], Optional[float]]:
    """
    Calculate the Simple Moving Average (SMA) for the given data and period.

    Args:
        data (pd.DataFrame): The historical stock data.
        period (int): The period over which to calculate the SMA.

    Returns:
        Tuple[Optional[float], Optional[float]]: The most recent and second most recent SMA values.
    """
    if 'close' not in data.columns:
        raise ValueError("The data must contain a 'close' column.")
    
    data_numeric = data['close']
    
    if len(data_numeric) < period:
        print(f"Not enough data to calculate SMA for period: {period}")
        return None, None
    
    sma = data_numeric.rolling(window=period).mean()
    return sma.iloc[-1], sma.iloc[-2] if len(sma) > 1 else (sma.iloc[-1], None)

def calculate_ema(data: pd.Series, period: int = 20) -> Tuple[Optional[float], Optional[float]]:
    """
    Calculate the Exponential Moving Average (EMA) for the given data and period.

    Args:
        data (pd.Series): The historical stock data.
        period (int): The period over which to calculate the EMA.

    Returns:
        Tuple[Optional[float], Optional[float]]: The most recent and second most recent EMA values.
    """
    # Ensure only numeric data is used for EMA calculation
    if not pd.api.types.is_numeric_dtype(data):
        data = pd.to_numeric(data, errors='coerce')

    if len(data) < period:
        print(f"Not enough data to calculate EMA for period: {period}")
        return None, None
    
    ema = data.ewm(span=period, adjust=False).mean()
    return ema.iloc[-1], ema.iloc[-2] if len(ema) > 1 else (ema.iloc[-1], None)

def calculate_trix(data: pd.Series, period: int = 15) -> Optional[float]:
    if len(data) < period:
        print(f"Not enough data to calculate TRIX for period: {period}")
        return None
    
    ema1 = data.ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    trix = 100 * (ema3.diff() / ema3.shift(1))
    return trix.iloc[-1] if not trix.empty else None

def calculate_aroon(high: pd.Series, low: pd.Series, period: int = 25) -> Tuple[Optional[float], Optional[float]]:
    if len(high) < period or len(low) < period:
        print(f"Not enough data to calculate Aroon for period: {period}")
        return None, None
    
    aroon_up = high.rolling(window=period).apply(lambda x: (x.argmax() + 1) * 100 / period, raw=True)
    aroon_down = low.rolling(window=period).apply(lambda x: (x.argmin() + 1) * 100 / period, raw=True)
    return aroon_up.iloc[-1], aroon_down.iloc[-1] if not aroon_up.empty and not aroon_down.empty else (None, None)

def calculate_elder_ray(high: pd.Series, low: pd.Series, close: pd.Series) -> Tuple[Optional[float], Optional[float]]:
    if len(high) < 13 or len(low) < 13 or len(close) < 13:
        print("Not enough data to calculate Elder Ray for period: 13")
        return None, None

    bull_power = high - close.ewm(span=13, adjust=False).mean()
    bear_power = low - close.ewm(span=13, adjust=False).mean()
    return bull_power.iloc[-1], bear_power.iloc[-1] if not bull_power.empty and not bear_power.empty else (None, None)

def calculate_heikin_ashi(open: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series) -> Optional[float]:
    if len(open) < 1 or len(high) < 1 or len(low) < 1 or len(close) < 1:
        print("Not enough data to calculate Heikin Ashi")
        return None

    ha_close = (open + high + low + close) / 4
    return None if ha_close.empty else ha_close.iloc[-1]

def calculate_rsi(data: pd.Series, period: int = 14) -> Optional[float]:
    if len(data) < period:
        print(f"Not enough data to calculate RSI for period: {period}")
        return None
    
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return None if rsi.empty else rsi.iloc[-1]

def calculate_parabolic_sar(close: pd.Series, low: pd.Series, high: pd.Series, af_start: float = 0.02, af_increment: float = 0.02, af_max: float = 0.2) -> pd.Series:
    if len(close) < 1 or len(low) < 1 or len(high) < 1:
        print("Not enough data to calculate Parabolic SAR")
        return pd.Series([None])

    psar = close.copy()
    psar.iloc[0] = low.iloc[0]
    uptrend = True
    af = af_start
    ep = high.iloc[0]

    for i in range(1, len(close)):
        if uptrend:
            psar.iloc[i] = psar.iloc[i - 1] + af * (ep - psar.iloc[i - 1])
            if low.iloc[i] < psar.iloc[i]:
                uptrend = False
                psar.iloc[i] = ep
                ep = low.iloc[i]
                af = af_start
        else:
            psar.iloc[i] = psar.iloc[i - 1] - af * (psar.iloc[i - 1] - ep)
            if high.iloc[i] > psar.iloc[i]:
                uptrend = True
                psar.iloc[i] = ep
                ep = high.iloc[i]
                af = af_start

        if uptrend:
            if high.iloc[i] > ep:
                ep = high.iloc[i]
                af = min(af + af_increment, af_max)
        else:
            if low.iloc[i] < ep:
                ep = low.iloc[i]
                af = min(af + af_increment, af_max)

    return psar

# Example usage within the main script
if __name__ == "__main__":
    ticker_symbol = 'AAPL'
    period = '1y'
    interval = '1d'

    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period=period, interval=interval)
    data.reset_index(inplace=True)
    data.set_index("Date", inplace=True)
    data = data.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })

    print("Historical Data")