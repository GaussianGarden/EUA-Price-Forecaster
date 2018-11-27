
def data_prepare(path):
    import os
    os.chdir(path)

    # CSV file reading
    import pandas as pd
    data = pd.read_csv("input.csv", sep=';', parse_dates=['Date'])

    # lagging values
    data.loc[:, data.columns[2:6]] = data.loc[:, data.columns[2:6]].shift(1)
    data.loc[:, data.columns[8:12]] = data.loc[:, data.columns[8:12]].shift(1)
    data.loc[:, data.columns[13:17]] = data.loc[:, data.columns[13:17]].shift(1)
    data.loc[:, data.columns[18:22]] = data.loc[:, data.columns[18:22]].shift(1)

    # log values
    import numpy as np
    data.loc[:, data.columns[np.r_[1:5, 7:11, 12:16, 17:21]]] = \
        data.loc[:, data.columns[np.r_[1:5, 7:11, 12:16, 17:21]]].applymap(lambda x:np.log(1+x))

      # price lags
    data['lag1'] = data["Settle"].shift(1)
    data['lag2'] = data["Settle"].shift(2)
    data['lag3'] = data["Settle"].shift(3)
    data['lag4'] = data["Settle"].shift(4)
    data['lag5'] = data["Settle"].shift(5)
    data['lag6'] = data["Settle"].shift(6)
    data['lag7'] = data["Settle"].shift(7)

    # additional features
    import ta as ta
    data['bollinger_high'] = ta.bollinger_hband(data["Settle"], n=20, ndev=2, fillna=True)
    data['bollinger_low'] = ta.bollinger_lband(data["Settle"], n=20, ndev=2, fillna=True)
    data['rsi20'] = ta.rsi(data["Settle"], n=20,  fillna=False)
    data['tsi20'] = ta.tsi(data["Settle"], r=25, s=13, fillna=False)
    data['macd'] = ta.macd(data["Settle"], n_fast=12, n_slow=26, fillna=False)
    data['ema'] = ta.ema_indicator(data["Settle"], n=12, fillna=False)
    
    # missing data
    data.loc[:, data.columns[1:]] = data.loc[:, data.columns[1:]].replace(0, np.NaN)
    data.loc[:, data.columns[1:]] = data.loc[:, data.columns[1:]].replace(np.NaN, data.loc[:, data.columns[1:]].mean())
    
    # delete first row
    data = data.drop(data.index[[0, 1, 2, 3, 4, 5, 6]])

    print(data.isnull().sum())
    data = data.reset_index(drop=True)
    return data



