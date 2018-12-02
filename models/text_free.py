# We will collect models from the Jupyter Notebooks here
import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense, Activation, BatchNormalization, Dropout


class KerasRegressorEnsemble(BaseEstimator, RegressorMixin):
    def __init__(self, input_dim, num_estimators=10, optimizer='adam', loss="mse", dropout_proba=0, epochs=500,
                 batch_size=128):
        self.dropout_proba = dropout_proba
        self.input_dim = input_dim
        self.optimizer = optimizer
        self.loss = loss
        self.num_estimators = num_estimators
        self.epochs = epochs
        self.batch_size = batch_size

        def make_model():
            model = Sequential([
                Dense(16, input_dim=self.input_dim),
                Activation('relu'),
                Dropout(self.dropout_proba),
                BatchNormalization(),
                Dense(8),
                Activation('relu'),
                Dense(1)
            ])
            model.compile(optimizer=optimizer, loss=loss)
            return model

        self.models = []
        self.model_maker = make_model

    def fit(self, X, y, *args, **kwargs):
        print("Training", self.num_estimators, "models for the ensemble with params",
              self.dropout_proba, self.optimizer, self.loss, self.epochs, self.batch_size, ".")
        if not self.models:
            self.models = [self.model_maker() for selection in
                           [np.random.choice(np.arange(len(X)), len(X)) for _ in range(self.num_estimators)]]
        for i, model in enumerate(self.models):
            print(f"Training model {i+1}.")
            model.fit(X, y, epochs=self.epochs, batch_size=self.batch_size, verbose=0)

    def predict(self, X):
        if not self.models:
            raise AttributeError
        return np.array([model.predict(X) for model in self.models]).mean(axis=0)

    def score(self, X, y_true, **kwargs):
        return mean_squared_error(y_true, self.predict(X), **kwargs)
