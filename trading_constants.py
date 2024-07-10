# Updated constants.py

# General Trading Parameters
stop_loss = 0.1
ema_cross_threshold = 0.02
max_investment_partition = 0.1
starting_account_value = 100000
trading_strategy_thread_count = 45

# Stock Lists
whitelist = [
    "AMZN", "RKT", "SNAP", "SPNY", "VEA", "BRK.B", "IBM", "JPM", 
    "META", "METV", "MSFT", "NTB", "NVDA", "PLTR", "PPA", "RIVN", "SPY", 
    "TBT", "UBER", "WMT", "AXP", "TEVA", "GOOGL", "RL", "SPXL", "V", "AAPL",
    "TSLA", "NFLX", "GOOG", "BABA", "CSCO", "INTC", "ADBE", "CRM", "ORCL",
    "PYPL", "NVDA", "AMD", "SHOP", "SQ", "ZM", "PINS", "DOCU", "PTON", 
    "TDOC", "BYND", "SNOW", "AAPL", "INTC", "FB", "GOOG", "^AORD", "ZIONW", "TCEHY", "JMPLF", 
    "FMCC", "CICHF", "CUK", "EBCOY", "C38U.SI", "AGM-A", "DNNGY", 
    "AOBC", "DKNG", "VST", "TIVO", "AVGO", "AMZN", "VGT", "MSFT", 
    "BABA", "TSLA", "NVDA", "AMD", "EA", "PYPL", "WORK"
]
blacklist = ['BTC-USD', '^N225']

# TRIX Strategy Parameters
trix_period = 15
trix_threshold = 0.1

# Aroon Strategy Parameters
aroon_period = 25
aroon_up_threshold = 50
aroon_down_threshold = 49

# Elder Ray Index Strategy Parameters
elder_ray_bull_threshold = 0.0
elder_ray_bear_threshold = 0.1

# Add any other strategy-specific parameters here