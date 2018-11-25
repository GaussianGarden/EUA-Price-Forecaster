
# load data
from Data_Preparation import data_prepare
data = data_prepare('/Users/Chris/Documents/GitHub/EUA-Price-Forecaster/Data')

# naive models OLS
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model

#for loop rolling window

for i in range (1, 24, 1):
    #data split into training and test
    x_train_180 = data.loc[i:180+i, data.columns[np.r_[1:3, 5:34]]]
    y_train_180 = data.loc[i:180+i, data.columns[4]]
    x_test_180 = data.loc[180+i, data.columns[np.r_[1:3, 5:34]]]
    y_test_180 = data.loc[180+i, data.columns[4]]
    
    #OLS model
    regr = linear_model.LinearRegression()
    regr.fit(x_train_180, y_train_180)
    

