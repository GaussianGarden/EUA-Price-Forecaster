import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def prepare_index(df):
    """
    Sort the index of a DataFrame in order to allow for time series related manipulations in pandas.
    :param df: A pandas DataFrame instance
    :return: df
    """
    return df.sort_index()


def drop_all_na(df):
    """
    Drop all rows in a DataFrame that contain at least one NA value
    :param df: A pandas DataFrame instance
    :return: df
    """
    return df.dropna(axis=0, how="any")


def replace_missing_values_as_of(df, resources):
    """
    Replace missing ".Open", ".Low" and ".High" values from the specified resources by using existing values.
    :param df: A pandas DataFrame instance
    :param resources: An iterable of strings that name the resources (e.g. "Coal"). This is case sensitive.
    :return: df
    """
    for resource in resources:
        missing = (df[resource + ".Open"] <= 0)
        df.loc[missing, resource + ".Open"] = (df[resource + ".Settle"].asof(
            df[missing].index.shift(-1, freq="d")).shift(1, freq="d"))
        high_missing = (df[resource + ".High"] <= 0)
        df.loc[high_missing, resource + ".High"] = np.max(
            df.loc[high_missing, [resource + ".Open", resource + ".Settle"]], axis=1)
        low_missing = (df[resource + ".Low"] <= 0)
        df.loc[low_missing, resource + ".Low"] = np.min(
            df.loc[low_missing, [resource + ".Open", resource + ".Settle"]], axis=1)
    return df


def prepare_change_columns(df):
    """
    Re-compute the change columns by using the previous settle values.
    :param df: A pandas DataFrame instance
    :return: df
    """
    change_cols = ["Change", "Gas.Change", "Coal.Change", "Oil.Change"]
    settle_cols = ["Settle", "Gas.Settle", "Coal.Settle", "Oil.Settle"]
    df[change_cols] = df[settle_cols].diff()
    df = df.iloc[1:]
    return df


def make_shifts(df):
    """
    Shift the "High", "Low", "Settle" and "Change" values to avoid data leaks.
    :param df: A pandas DataFrame instance
    :return: df
    """
    for name in ("", "Gas.", "Coal.", "Oil."):
        cols = [name + val for val in ("High", "Low", "Settle", "Change")]
        new_cols = ["Prev. Day " + col for col in cols]
        df[new_cols] = df[cols].shift(1)
        df = df.drop(columns=[col for col in cols if col != "Settle"])
    df = df.iloc[1:]
    return df


def chain_preparations(df):
    """
    Perform the preparations steps above sequentially.
    :param df: A pandas DataFrame instance
    :return: df
    """
    df = prepare_index(df)
    df = drop_all_na(df)
    df = replace_missing_values_as_of(df, ["Coal"])
    df = prepare_change_columns(df)
    df = make_shifts(df)
    return df


def plot_univariate_distributions(df, columns, ncols=3):
    """
    Make plots of the univariate distributions of the specified columns of a given dataframe.
    :param df: A pandas DataFrame instance
    :param columns: An iterable of strings indicating the desired columns of the dataframe to plot.
    :param ncols: The number of columns in the resulting plot.
    :return: None
    """
    nrows = int(np.ceil(len(columns) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 6, nrows * 6))
    axes = axes.reshape(-1, ncols)
    plt.subplots_adjust(wspace=0.3, hspace=0.3)
    last_used_col = 0
    for i, col in enumerate(columns):
        cur_col_number = i % ncols
        ax = axes[(i // ncols, cur_col_number)]
        sns.distplot(df[col].values, ax=ax)
        ax.set_title(col)
        last_used_col = cur_col_number
    for i in range(last_used_col + 1, ncols):
        fig.delaxes(axes[-1, i])


def log_prices(df):
    """
    Replace prices by their log values. A column is chosen if it contains at least one of the strings "Open", "High",
    "Low" or "Settle" and does not contain "Interest".
    :param df: A pandas DataFrame instance
    :return: df
    """
    loggable_columns = [col for col in df.columns if any(word in col for word in ("Open", "High", "Low", "Settle"))
                        and "Interest" not in col]
    df[loggable_columns] = (df[loggable_columns] + 1).apply(np.log)
    return df
