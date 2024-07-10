import stock_data_gatherer as sdg
import util
def moving_average_checker(ticker_symbol) -> int:
    stock_status = sdg.get_current_stock_data(ticker_symbol)
    if stock_status['Close'] > stock_status['EMA'] and stock_status['PREVPRICE'] < stock_status['PREVSMA']:
        return 0.3
    elif stock_status['Close'] < stock_status['SMA'] and stock_status['PREVPRICE'] > stock_status['PREVSMA']:
        return -0.3
    return 0

def volume_checker(ticker_symbol) -> int:
    stock_status = sdg.get_current_stock_data(ticker_symbol)
    try:
        volume = sdg.get_volume_slope(ticker_symbol) / (0.2 * stock_status['Volume'])
    except ZeroDivisionError:
        volume = 0
    try:
        price = sdg.get_price_slope(ticker_symbol) / (0.2 * stock_status['Close'])
    except ZeroDivisionError:
        price = 0

    print(ticker_symbol, ": Price: ", price, " Volume: ", volume)
    if price > 0.04 and volume > 1:
        return 0.2
    elif price < -0.03 and volume > 0.8:
        return -0.2
    return 0

def trix_checker(ticker_symbol) -> int:
    stock_status = sdg.get_current_stock_data(ticker_symbol)
    trix_current = stock_status['TRIX']
    trix_previous = stock_status['PREVTRIX']
    if trix_current > 0 and trix_previous <= 0:
        return 0.5
    elif trix_current < 0 and trix_previous >= 0:
        return -0.5
    return 0

def aroon_checker(ticker_symbol) -> int:
    stock_status = sdg.get_current_stock_data(ticker_symbol)
    aroon_up = stock_status['AROON_UP']
    aroon_down = stock_status['AROON_DOWN']
    if aroon_up > 70 and aroon_down < 30:
        return 0.3
    elif aroon_up < 30 and aroon_down > 70:
        return -0.3
    return 0

def elder_ray_checker(ticker_symbol) -> int:
    stock_status = sdg.get_current_stock_data(ticker_symbol)
    bull_power = stock_status['BULL_POWER']
    bear_power = stock_status['BEAR_POWER']
    if bull_power > 0 and bear_power < 0:
        return 0.4
    elif bull_power < 0 and bear_power > 0:
        return -0.4
    return 0

def heikin_ashi_checker(ticker_symbol) -> int:
    stock_status = sdg.get_current_stock_data(ticker_symbol)
    heikin_ashi_close = stock_status['HEIKIN_ASHI_CLOSE']
    if stock_status['Close'] > heikin_ashi_close:
        return 0.4
    elif stock_status['Close'] < heikin_ashi_close:
        return -0.4
    return 0

def rapid_rebound_checker(ticker_symbol) -> int:
    stock_data = sdg.get_current_stock_data(ticker_symbol)
    historical_data = sdg.get_historical_data(ticker_symbol, '1y', '1d')  # Adjust the period and interval as needed

    if (util.calculate_price_drop(historical_data, 0.03) and
        util.calculate_volume_spike(historical_data, 1.5) and
        util.calculate_rsi(historical_data, 14) < 30):
        return 0.5
    return 0

def parabolic_sar_checker(ticker_symbol) -> int:
    stock_status = sdg.get_current_stock_data(ticker_symbol)
    if stock_status['Close'] > stock_status['PSAR']:
        return 0.4
    elif stock_status['Close'] < stock_status['PSAR']:
        return -0.4
    return 0

def combined_strategy(ticker_symbol) -> float:
    score = 0
    score += moving_average_checker(ticker_symbol)
    score += volume_checker(ticker_symbol)
    score += trix_checker(ticker_symbol)
    score += aroon_checker(ticker_symbol)
    score += elder_ray_checker(ticker_symbol)
    score += heikin_ashi_checker(ticker_symbol)
    score += rapid_rebound_checker(ticker_symbol)
    score += parabolic_sar_checker(ticker_symbol)
    return score