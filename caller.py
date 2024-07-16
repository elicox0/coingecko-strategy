import os
import datetime
from typing import Optional

class ApiCaller():
    """
    Handles API calls by determining the time needed between each 
    API call to stay within per-minute and monthly call limit.
    
    Makes calls when told.

    Manages persistent storage of remaining call counts.
    """
    MAX_CALLS_PER_MONTH = 10_000
    MAX_CALLS_PER_MINUTE = 30
    MIN_SECONDS_BETWEEN_CALLS = 256 # If running for >= 1 mo.
    MIN_SECONDS_BETWEEN_CALLS_SHORT = 2  # If running for >= 1 min << 1 mo.

    def __init__(self, 
                 api_key:str, 
                 calls_tracker_file:str,
                 monthly_remaining_calls:Optional[int]) -> None:
        self.api_key = api_key
        self.calls_tracker_file = calls_tracker_file
        self.set_monthly_remaining_calls(monthly_remaining_calls)
    
    def set_monthly_remaining_calls(self, input:Optional[int]) -> None:
        """
        Setter for the amount of calls that can be made before the
        month rolls over. Used to determine the time between calls.

        Prioritize command-line argument of remaning calls,
        then number of calls saved on disk, then default to class const.
        """
        if input is not None:
            self.monthly_remaining_calls = input
        elif os.path.exists(self.calls_tracker_file):
            with open(self.calls_tracker_file, "r") as fin:
                self.monthly_remaining_calls = int(fin.readline())
            return # no need to write to disk if we just read it
        else:
            self.monthly_remaining_calls = self.MAX_CALLS_PER_MONTH
        self.write_monthly_remaining_calls()

    def write_monthly_remaining_calls(self):
        """
        Write to disk.
        """
        if not os.path.exists(self.calls_tracker_file):
            print(f"Persistent tracker for remaining calls does not exist. Creating at {self.calls_tracker_file}")
        with open(self.calls_tracker_file, 'w') as fout:
            fout.write(str(self.monthly_remaining_calls))

    def get_seconds_left_in_month(self):
        """
        Determine seconds left until the month rolls over.
        """
        today = datetime.datetime.today()
        next_month_start = datetime.datetime(today.year, today.month + 1, 1)
        time_to_next_month = next_month_start - today
        return time_to_next_month.total_seconds()

    def set_seconds_between_calls(self) -> None:
        """
        Setter method to determine how long to wait between API calls.

        Convert remaining calls per month to calls per second
        (how many seconds left in the month?) then wait at least
        that long and at least MIN_SECONDS_BETWEEN_CALLS.
        """
        seconds_between_calls = self.monthly_remaining_calls / self.get_seconds_left_in_month()
        self.seconds_between_calls = max(seconds_between_calls, self.MIN_SECONDS_BETWEEN_CALLS)

if __name__ == "__main__":
    pass
