import pandas as pd
import stock_data_gatherer as sdg
import util
import logging

def moving_average_checker(stock_info: dict, ticker_symbol: str) -> float:
    if all(key in stock_info for key in ['Close', 'EMA', 'PREVPRICE', 'PREVSMA']):
        if stock_info['Close'] > stock_info['EMA'] and stock_info['PREVPRICE'] < stock_info['PREVSMA']:
            logging.info(f"Ticker: {ticker_symbol} - Buy signal: Close > EMA and PREVPRICE < PREVSMA")
            return 0.3
        elif stock_info['Close'] < stock_info['SMA'] and stock_info['PREVPRICE'] > stock_info['PREVSMA']:
            logging.info(f"Ticker: {ticker_symbol} - Sell signal: Close < SMA and PREVPRICE > PREVSMA")
            return -0.3
    logging.info(f"Ticker: {ticker_symbol} - No significant signal")
    return 0.0

def volume_checker(stock_info, ticker_symbol) -> int:
    historical_data = sdg.get_historical_data(ticker_symbol, '1mo', '1d')
    if not isinstance(historical_data, pd.DataFrame):
        logging.error(f"Expected historical data to be a pandas DataFrame for {ticker_symbol}")
        return 0
    
    if 'Volume' not in historical_data.columns:
        logging.error(f"DataFrame for {ticker_symbol} must contain 'Volume' column")
        return 0
    
    volume_slope = util.calculate_volume_slope(historical_data)
    return volume_slope / (0.2 * stock_info['Volume']) if 'Volume' in stock_info else 0
def trix_checker(ticker_symbol, stock_info) -> int:
    if stock_info['TRIX'] is not None and stock_info['PREVTRIX'] is not None:
        trix_current = stock_info['TRIX']
        trix_previous = stock_info['PREVTRIX']
        if trix_current > 0 and trix_previous <= 0:
            return 0.5
        elif trix_current < 0 and trix_previous >= 0:
            return -0.5
    return 0

def aroon_checker(ticker_symbol, stock_info) -> int:
    if stock_info['AROON_UP'] is not None and stock_info['AROON_DOWN'] is not None:
        aroon_up = stock_info['AROON_UP']
        aroon_down = stock_info['AROON_DOWN']
        if aroon_up > 70 and aroon_down < 30:
            return 0.3
        elif aroon_up < 30 and aroon_down > 70:
            return -0.3
    return 0

def elder_ray_checker(ticker_symbol, stock_info) -> int:
    if stock_info['BULL_POWER'] is not None and stock_info['BEAR_POWER'] is not None:
        bull_power = stock_info['BULL_POWER']
        bear_power = stock_info['BEAR_POWER']
        if bull_power > 0 and bear_power < 0:
            return 0.4
        elif bull_power < 0 and bear_power > 0:
            return -0.4
    return 0

def heikin_ashi_checker(ticker_symbol, stock_info) -> int:
    if stock_info['HEIKIN_ASHI_CLOSE'] is not None:
        heikin_ashi_close = stock_info['HEIKIN_ASHI_CLOSE']
        if stock_info['Close'] > heikin_ashi_close:
            return 0.4
        elif stock_info['Close'] < heikin_ashi_close:
            return -0.4
    return 0

def rapid_rebound_checker(ticker_symbol, stock_info) -> int:
    if stock_info['Open'] is not None and stock_info['Close_Prev'] is not None and stock_info['Volume'] is not None and stock_info['Volume_Prev'] is not None and stock_info['RSI'] is not None and (stock_info['Open'] < (1 - 0.03) * stock_info['Close_Prev'] and
                stock_info['Volume'] > 1.5 * stock_info['Volume_Prev'] and
                stock_info['RSI'] < 30):
        return 0.5
    return 0

def parabolic_sar_checker(ticker_symbol, stock_info) -> int:
    if stock_info['PSAR'] is not None:
        if stock_info['Close'] > stock_info['PSAR']:
            return 0.4
        elif stock_info['Close'] < stock_info['PSAR']:
            return -0.4
    return 0
def combined_strategy(ticker_symbol, stock_info) -> float:
    score = 0
    score += moving_average_checker(ticker_symbol, stock_info)
    score += volume_checker(ticker_symbol, stock_info)
    score += trix_checker(ticker_symbol, stock_info)
    score += aroon_checker(ticker_symbol, stock_info)
    score += elder_ray_checker(ticker_symbol, stock_info)
    score += heikin_ashi_checker(ticker_symbol, stock_info)
    score += rapid_rebound_checker(ticker_symbol, stock_info)
    score += parabolic_sar_checker(ticker_symbol, stock_info)
    return score