import sqlite3
import pandas as pd

from .provided_code import data_manager

def get_df():
    con = sqlite3.connect("coins.db")
    # cursor = con.cursor()
    return pd.read_sql_query("SELECT * FROM MARKET", con)

def strategy(df):
    timestamps = []
    signals = []
    return timestamps, signals

#df = get_df()
#df.info()

if __name__ == "__main__":
    df = data_manager.get_data()
    df.info()

