import sqlite3
import pandas as pd
import numpy as np

import data_manager, simple_backtester

def get_df():
    con = sqlite3.connect("coins.db")
    # cursor = con.cursor()
    return pd.read_sql_query("SELECT * FROM MARKET", con)

def strategy(df):
    df.info()
    signals = np.ones(df.shape[0])
    timestamps = np.zeros_like(signals)
    return timestamps, signals


if __name__ == "__main__":
    df = data_manager.get_data()
    timestamps, signals = strategy(df)
    print(simple_backtester.simple_backtest(
        df,timestamps,signals)['end_portfolio_value']
    )
                           
