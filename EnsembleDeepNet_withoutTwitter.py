# load data
from Data_Preparation import data_prepare
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.preprocessing import StandardScaler
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

data = data_prepare('/Users/Chris/Documents/GitHub/EUA-Price-Forecaster/Data')


# define base model one
def baseline_model_1():
    # create model
    model = Sequential()
    model.add(Dense(32, input_dim=32, kernel_initializer='normal', activation='relu'))
    model.add(Dense(16, kernel_initializer='normal', activation='relu'))
    model.add(Dense(8, kernel_initializer='normal', activation='relu'))
    model.add(Dense(1, kernel_initializer='normal'))
    # Compile model
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model


# define base model one
def baseline_model_2():
    # create model
    model = Sequential()
    model.add(Dense(32, input_dim=32, kernel_initializer='normal', activation='relu'))
    model.add(Dense(15, kernel_initializer='normal', activation='relu'))
    model.add(Dense(1, kernel_initializer='normal'))
    # Compile model
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model


# for loop rolling window initialize result vector
col_names = ['Date', 'Observation', 'Forecast_1', 'Forecast_2', 'Ensemble']
results = pd.DataFrame(columns=col_names)

for i in range(0, 3, 1):  # 806
    # data split into training and test / 180 days
    x_train_180 = data.loc[i:180 + i, data.columns[np.r_[2:3, 5:36]]]
    y_train_180 = data.loc[i:180 + i, data.columns[4]]
    x_test_180 = data.loc[180 + i, data.columns[np.r_[2:3, 5:36]]].values.reshape(-1, 32)
    y_test_180 = data.loc[180 + i, data.columns[4]]
    test_date = data.loc[180 + i, data.columns[0]]

    # fix random seed for reproducibility
    seed = 7
    np.random.seed(seed)

    # evaluate model with standardized data set
    scaler = StandardScaler()
    scaler.fit(x_train_180)
    x_train_180 = scaler.transform(x_train_180)
    x_test_180 = scaler.transform(x_test_180)

    # build Keras/TensorFlow Model one
    estimator_1 = KerasRegressor(build_fn=baseline_model_1, epochs=100, batch_size=5,
                                 verbose=True)
    estimator_1.fit(x_train_180, y_train_180)
    estimate_1 = estimator_1.predict(x_test_180)
    # Rescale from Log to Normal
    estimate_1 = np.exp(estimate_1) - 1

    # build Keras/TensorFlow Model two
    estimator_2 = KerasRegressor(build_fn=baseline_model_2, epochs=120, batch_size=5,
                                 verbose=True)
    estimator_2.fit(x_train_180, y_train_180)
    estimate_2 = estimator_2.predict(x_test_180)
    # Rescale from Log to Normal
    estimate_2 = np.exp(estimate_2) - 1

    # create ensemble
    estimate_ensemble = (estimate_1 + estimate_2)/2
    # save predictions and observations
    results.loc[len(results)] = [test_date, np.exp(y_test_180) - 1, estimate_1, estimate_2, estimate_ensemble]
