import pandas as pd
import os
import json
import requests
from . import CONFIG


class AlphaVantage:

    TOKEN = CONFIG.ALPHA_VANTAGE_KEY
    DATA_DIR = f"{CONFIG.DATA_LOCATION}/AVData"

    def __init__(self, **kwargs):
        self.ticker = kwargs.get('ticker')
        self.save = kwargs.get('save', True)
        self.local_only = kwargs.get('local_only', False)
        self.annual_earnings = None
        self.quarterly_earnings = None
        self._earnings = None
        if kwargs.get('auto_load_earnings', False):
            self.load_earnings()

    @property
    def ticker(self):
        return self._ticker

    @ticker.setter
    def ticker(self, tick):
        if isinstance(tick, str):
            self._ticker = tick.upper()
        else:
            # No Error - useful for batching.
            self._ticker = None

    @property
    def earnings_filename(self):
        return f"{self.DATA_DIR}/{self.ticker}_earnings.json"

    @classmethod
    def save_data(cls, data, title):
        fname = f"{cls.DATA_DIR}/{title}.json"
        with open(fname, "w+") as f:
            json.dump(data, f, indent=4)
        print(f"saved alpha vantage data: {fname}")

    def get_json(self, fname):
        if os.path.exists(fname):
            with open(fname) as f:
                return json.load(f)
        return None

    def fetch_earnings(self):
        response = requests.get(
            f"https://www.alphavantage.co/query?function=EARNINGS&symbol={self.ticker}&apikey={self.TOKEN}")
        response.raise_for_status()
        return response.json()

    def merge_earnings(self, fetched_earnings):
        annual_dates = [item.get('fiscalDateEnding')
                        for item in self._earnings["annualEarnings"]]
        quarter_dates = [item.get('reportedDate')
                         for item in self._earnings["quarterlyEarnings"]]
        #
        for annual in fetched_earnings.get("annualEarnings", []):
            if annual.get('fiscalDateEnding') not in annual_dates:
                self._earnings["annualEarnings"].append(annual)
        #
        for quarter in fetched_earnings.get("quarterlyEarnings", []):
            if quarter.get('reportedDate') not in quarter_dates:
                self._earnings["quarterlyEarnings"].append(quarter)

    def update_earnings(self, fname):
        self._earnings = self.get_json(fname)
        if self._earnings is None:
            self._earnings = self.fetch_earnings()
        elif not self.local_only:
            fetched_earnings = self.fetch_earnings()
            self.merge_earnings(fetched_earnings)
        if self.save:
            title = f"{self.ticker}_earnings"
            self.save_data(self._earnings, title)

    def load_earnings(self):
        fname = self.earnings_filename
        self.update_earnings(fname)
        self.annual_earnings = pd.DataFrame(self._earnings["annualEarnings"])
        self.quarterly_earnings = pd.DataFrame(
            self._earnings["quarterlyEarnings"])
