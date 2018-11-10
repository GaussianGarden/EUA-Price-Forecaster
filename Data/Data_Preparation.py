#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#change working directory
import os
print(os.getcwd())
os.chdir('/Users/Chris/Documents/GitHub/EUA-Price-Forecaster/Data')

"CSV file reading"
import pandas as pd 
data = pd.read_csv("input.csv",sep=';') 

"missing data"
import numpy
# mark zero values as missing or NaN
data.iloc[2:26] = data.iloc[2,:26].replace(0, numpy.NaN)
# fill missing values with mean column values
data.iloc[2:26].fillna(data.iloc[2:26].mean(), inplace=True)
# count the number of NaN values in each column
print(data.isnull().sum())