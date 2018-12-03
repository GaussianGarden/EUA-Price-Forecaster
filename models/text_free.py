# We will collect models from the Jupyter Notebooks here
import os
from keras.models import Sequential
from keras.layers import Dense, Activation, BatchNormalization, Dropout
from keras.engine.saving import load_model
import numpy as np
import re


def simple_nn(input_dim, dropout_proba=0, optimizer="adam", loss="mse"):
    """

    :param input_dim:
    :param dropout_proba:
    :param optimizer:
    :param loss:
    :return:
    """
    model = Sequential([
        Dense(16, input_dim=input_dim),
        Activation('relu'),
        Dropout(dropout_proba),
        BatchNormalization(),
        Dense(8),
        Activation('relu'),
        Dense(1)
    ])
    model.compile(optimizer=optimizer, loss=loss)
    return model


class KerasEnsemble:
    """

    """
    def __init__(self, models):
        """

        :param models:
        """
        self.models = models

    def fit(self, X, y, epochs=10, batch_size=128):
        """

        :param X:
        :param y:
        :param epochs:
        :param batch_size:
        :return:
        """
        for model in self.models:
            model.fit(X, y, epochs, batch_size)

    def predict(self, X):
        """

        :param X:
        :return:
        """
        return np.mean([model.predict(X) for model in self.models], axis=0)

    def save(self, directory, file_name):
        """

        :param directory:
        :param file_name:
        :return:
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
        for i, model in enumerate(self.models):
            model.save(os.path.join(directory, file_name + "_" + str(i) + ".h5"))

    @staticmethod
    def load(directory, name):
        """
        
        :param directory:
        :param name:
        :return:
        """
        saved_model_pattern = re.compile(name + r"_(?P<num>(\d+)).h5", re.IGNORECASE)
        model_files = []
        for file in os.scandir(directory):
            match = saved_model_pattern.match(file.name)
            if match:
                model_files.append((int(match["num"]), file))
        if not model_files:
            raise RuntimeError("No model to load.")
        model_files.sort()
        if model_files[0][0] != 0 or model_files[-1][0] != len(model_files) - 1:
            raise RuntimeError("Inconsistent naming of model saves.")
        return KerasEnsemble([load_model(os.path.join(directory, file.name)) for num, file in model_files])
