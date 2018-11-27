# load data
from Data_Preparation import data_prepare
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
import os

os.environ['KMP_DUPLICATE_LIB_OK']='True'

data = data_prepare('/Users/Chris/Documents/GitHub/EUA-Price-Forecaster/Data')


# define base model
def baseline_model():
    # create model
    model = Sequential()
    model.add(Dense(32, input_dim=32, kernel_initializer='normal', activation='relu'))
    model.add(Dense(1, kernel_initializer='normal'))
    # Compile model
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model


# for loop rolling window

# for i in range (1, 24, 1):
# data split into training and test
i=1
x_train_180 = data.loc[i:180 + i, data.columns[np.r_[2:3, 5:36]]]
y_train_180 = data.loc[i:180 + i, data.columns[4]]
x_test_180 = data.loc[180 + i, data.columns[np.r_[2:3, 5:36]]]
y_test_180 = data.loc[180 + i, data.columns[4]]

# fix random seed for reproducibility
seed = 7
np.random.seed(seed)
# evaluate model with standardized dataset
estimator = KerasRegressor(build_fn=baseline_model, epochs=100, batch_size=5,
                           verbose=0)
kfold = KFold(n_splits=10, random_state=seed)
results = cross_val_score(estimator, x_train_180, y_train_180, cv=kfold)
print("Results: %.2f (%.2f) MSE" % (results.mean(), results.std()))
