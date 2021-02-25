import numpy as np
import pandas as pd
from datetime import datetime

dates = pd.date_range(datetime.strptime('10/10/2018', '%m/%d/%Y'), periods=100, freq='D')
close_prices = np.arange(len(dates))

close = pd.Series(close_prices, dates)
print(close.rolling(window=10).mean()[10:].head())
