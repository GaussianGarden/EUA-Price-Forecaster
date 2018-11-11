
def data_prepare(path):
    import os
    os.chdir(path)

    "CSV file reading"
    import pandas as pd
    data = pd.read_csv("input.csv", sep=';', parse_dates=['Date'])

    "lagging values"
    data.loc[:, data.columns[2:6]] = data.loc[:, data.columns[2:6]].shift(1)
    data.loc[:, data.columns[9:13]] = data.loc[:, data.columns[9:13]].shift(1)
    data.loc[:, data.columns[15:19]] = data.loc[:, data.columns[15:19]].shift(1)
    data.loc[:, data.columns[21:25]] = data.loc[:, data.columns[21:25]].shift(1)

    'missing data'
    import numpy as np
    data.loc[:, data.columns[1:]] = data.loc[:, data.columns[1:]].replace(0, np.NaN)
    data.loc[:, data.columns[1:]] = data.loc[:, data.columns[1:]].replace(np.NaN, data.loc[:, data.columns[1:]].mean())
    print(data.isnull().sum())

    "alternative"
    import statsmodels as sd





data_prepare('/Users/Chris/Documents/GitHub/EUA-Price-Forecaster/Data')
