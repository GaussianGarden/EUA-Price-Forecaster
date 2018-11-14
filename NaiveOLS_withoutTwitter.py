
# load data
from Data_Preparation.py import data_prepare
data_prepare('/Users/Chris/Documents/GitHub/EUA-Price-Forecaster/Data')

# naive models OLS
import pandas as pd
model = pd.stats.ols.MovingOLS(y=data.loc[:, data.columns[4]],
                               x=data.loc[:, data.columns[np.r_[1:3, 5:34]]],
                               window_type='rolling', window=100, intercept=True)
data['prediction'] = model.y_predict