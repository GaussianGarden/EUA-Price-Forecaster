#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#change working directory
import os
print(os.getcwd())
os.chdir('/Users/Chris/Documents/GitHub/EUA-Price-Forecaster/Data')

"CSV file reading"
import pandas as pd 
data = pd.read_csv("input.csv",sep=';',parse_dates=['Date']) 

"missing data"
import numpy as np
data.loc[:, data.columns[1:]] = data.loc[:, data.columns[1:]].replace(0, np.NaN)
data.loc[:, data.columns[1:]] = data.loc[:, data.columns[1:]].replace(np.NaN, data.loc[:, data.columns[1:]].mean())
print(data.isnull().sum())

data.info()
