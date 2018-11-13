
def data_prepare(path):
    import os
    os.chdir(path)

    # CSV file reading
    import pandas as pd
    data = pd.read_csv("input.csv", sep=';', parse_dates=['Date'])

    # lagging values
    data.loc[:, data.columns[2:6]] = data.loc[:, data.columns[2:6]].shift(1)
    data.loc[:, data.columns[9:13]] = data.loc[:, data.columns[9:13]].shift(1)
    data.loc[:, data.columns[15:19]] = data.loc[:, data.columns[15:19]].shift(1)
    data.loc[:, data.columns[21:25]] = data.loc[:, data.columns[21:25]].shift(1)
    
    # price lags
    data['lag1'] = data["Settle"].shift(1)
    data['lag2'] = data["Settle"].shift(2)
    data['lag3'] = data["Settle"].shift(3)
    data['lag4'] = data["Settle"].shift(4)
    data['lag5'] = data["Settle"].shift(5)
    data['lag6'] = data["Settle"].shift(6)
    data['lag7'] = data["Settle"].shift(7)

    # log values
    import numpy as np
    data.loc[:, data.columns[1:5]] = data.loc[:, data.columns[1:5]].apply(np.log)
    data.loc[:, data.columns[8:12]] = data.loc[:, data.columns[8:12]].apply(np.log)
    data.loc[:, data.columns[14:18]] = data.loc[:, data.columns[14:18]].apply(np.log)
    data.loc[:, data.columns[20:24]] = data.loc[:, data.columns[20:24]].apply(np.log)

    # missing data
    data.loc[:, data.columns[1:]] = data.loc[:, data.columns[1:]].replace(0, np.NaN)
    data.loc[:, data.columns[1:]] = data.loc[:, data.columns[1:]].replace(np.NaN, data.loc[:, data.columns[1:]].mean())
    # log scale of data

    # additional features
    import ta as ta
    data['bollinger_high'] = ta.bollinger_hband(data["Settle"], n=20, ndev=2, fillna=True)
    data['bollinger_low'] = ta.bollinger_lband(data["Settle"], n=20, ndev=2, fillna=True)
    data['rsi20'] = ta.rsi(data["Settle"], n=20,  fillna=False)
    data['tsi20'] = ta.tsi(data["Settle"], r=25, s=13, fillna=False)
    data['macd'] = ta.macd(data["Settle"], n_fast=12, n_slow=26, fillna=False)
    data['ema'] = ta.ema_indicator(data["Settle"], n=12, fillna=False)
    
    # delete first row
    data = data.drop(data.index[[0, 1, 2, 3, 4, 5, 6]])

    print(data.isnull().sum())
    return data


data_prepare('/Users/Chris/Documents/GitHub/EUA-Price-Forecaster/Data')
