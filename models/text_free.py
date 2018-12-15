# We will collect models from the Jupyter Notebooks here
from keras import regularizers
from keras.models import Sequential
from keras.layers import Dense, Activation, BatchNormalization, Dropout


def simple_nn(input_dim, dropout_proba=0, kernel_regularizer_lambda=0, optimizer="adam", loss="mse"):
    """

    :param kernel_regularizer_lambda: The L2 penalty on the non-bias weights.
    :param input_dim:
    :param dropout_proba:
    :param optimizer:
    :param loss:
    :return:
    """
    model = Sequential([
        Dense(16, input_dim=input_dim, kernel_regularizer=regularizers.l2(kernel_regularizer_lambda)),
        Activation('relu'),
        Dropout(dropout_proba),
        BatchNormalization(),
        Dense(8, kernel_regularizer=regularizers.l2(kernel_regularizer_lambda)),
        Activation('relu'),
        Dense(1, kernel_regularizer=regularizers.l2(kernel_regularizer_lambda))
    ])
    model.compile(optimizer=optimizer, loss=loss)
    return model
