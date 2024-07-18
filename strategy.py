import sqlite3
import pandas as pd

from provided_code import data_manager

def get_df():
    con = sqlite3.connect("coins.db")
    # cursor = con.cursor()
    df = pd.read_sql_query("SELECT * FROM MARKET", con)
    df.info()

def strategy(df):
    timestamps = []
    signals = []
    return timestamps, signals

get_df()

