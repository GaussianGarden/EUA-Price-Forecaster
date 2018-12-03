# We will collect models from the Jupyter Notebooks here
from keras.models import Sequential
from keras.layers import Dense, Activation, BatchNormalization, Dropout


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
