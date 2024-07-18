import os
import sys
import time
import datetime
import requests
from requests.models import HTTPError
import sqlite3
import json
from typing import Optional 

class ApiCaller():
    """
    Handles API calls by determining the time needed between each 
    API call to stay within per-minute and monthly call limit.
    
    Makes calls when told.

    Manages persistent storage of remaining call counts.
    """
    API_KEY = os.environ['CG_API_KEY']
    MAX_CALLS_PER_MONTH = 10_000
    MAX_CALLS_PER_MINUTE = 30
    MIN_SECONDS_BETWEEN_CALLS = 2 # to stay within 30 calls per minute

    def __init__(self, 
                 calls_tracker_file:str,
                 monthly_remaining_calls:Optional[int]) -> None:
        self.calls_tracker_file = calls_tracker_file

        if monthly_remaining_calls is not None:
            self.set_monthly_remaining_calls(monthly_remaining_calls)
        elif os.path.exists(self.calls_tracker_file):
            with open(self.calls_tracker_file, "r") as fin:
                self.set_monthly_remaining_calls(int(fin.readline()))
        else:
            self._monthly_remaining_calls = self.MAX_CALLS_PER_MONTH

        self.set_seconds_between_calls()
        self.con = sqlite3.connect("coins.db")
        self.cursor = self.con.cursor()
    
    def set_monthly_remaining_calls(self, calls:int) -> None:
        """
        Setter for the amount of calls that can be made before the
        month rolls over. Used to determine the time between calls.

        Prioritize argument of remaning calls,
        then number of calls saved on disk, then default to class const.

        Now handled in constructor
        """
        self._monthly_remaining_calls = calls

    def write_monthly_remaining_calls(self) -> None:
        """
        Write to disk.
        """
        if not os.path.exists(self.calls_tracker_file):
            print(f"Persistent tracker for remaining calls does not exist. Creating at {self.calls_tracker_file}")
        with open(self.calls_tracker_file, 'w') as fout:
            fout.write(str(self._monthly_remaining_calls))

    def get_seconds_left_in_month(self) -> int:
        """
        Determine seconds left until the month rolls over.
        """
        today = datetime.datetime.today()
        next_month_start = datetime.datetime(today.year, today.month + 1, 1)
        time_to_next_month = next_month_start - today
        return int(time_to_next_month.total_seconds()) + 1

    def set_seconds_between_calls(self) -> None:
        """
        Setter method to determine how long to wait between API calls.

        Convert remaining calls per month to calls per second
        (how many seconds left in the month?) then wait at least
        that long and at least MIN_SECONDS_BETWEEN_CALLS.
        """
        seconds_between_calls = self._monthly_remaining_calls / self.get_seconds_left_in_month()
        self.seconds_between_calls = max(seconds_between_calls, self.MIN_SECONDS_BETWEEN_CALLS)
        print(f"Waiting {self.seconds_between_calls} seconds between calls")

    def __call__(self, endpoint) -> None:
        response = requests.get(
                endpoint,
                headers = {
                    'accept': 'application/json',
                    'x-cg-demo-api-key': self.API_KEY,
                    'User-Agent': 'Mozilla/5.0'
                },
                params = {
                    'vs_currency': 'usd',
                    'ids': 'bitcoin, ethereum, solana, binancecoin'
                })
        self.set_monthly_remaining_calls(self._monthly_remaining_calls - 1)
        # time.sleep(self.seconds_between_calls)
        if response.status_code == 200:
            self.write_content_to_db(response.json())
        else:
            raise HTTPError(f"Received response {response.status_code}")
        time.sleep(10)

    def write_content_to_db(self, content:bytes) -> None:
        # obj = json.dumps(content)
        obj = content
        columns = [
             'id', 'symbol', 'name', 'image',\
             'current_price', 'market_cap',\
             'market_cap_rank', 'fully_diluted_valuation',\
             'total_volume', 'high_24h', 'low_24h',\
             'price_change_24h', 'price_change_percentage_24h',\
             'circulating_supply', 'total_supply', 'max_supply',\
             'ath', 'ath_change_percentage', 'ath_date', 'atl',\
             'atl_change_percentage', 'atl_date', 'roi', 'last_updated'
        ]
        query = "INSERT INTO MARKET VALUES (" + "?,"*23 + "?)" 
        for coin in obj:
            print("Adding response to database")
            self.cursor.execute(query, tuple(str(coin[key]) for key in columns))
        self.con.commit()

if __name__ == "__main__":
    input = int(sys.argv[1]) if len(sys.argv) > 1 else None
    caller = ApiCaller("./remaining_calls.txt", input)
    caller.cursor.execute("INSERT INTO MARKET VALUES (" + "?,"*23 + "?)", [123]*24)
    try:
        while True: caller("https://api.coingecko.com/api/v3/coins/markets")
    finally:
        caller.write_monthly_remaining_calls()
        caller.con.close()
