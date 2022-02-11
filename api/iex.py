import pandas as pd
import os
import json
import requests
from datetime import datetime
from .connections import Mongo
from . import CONFIG


class IEX:

    TOKEN = CONFIG.IEX_TOKEN
    _DB_NAME = CONFIG.DB_NAME
    DATA_DIR = os.path.join(CONFIG.DATA_LOCATION, '/IEXData')

    def __init__(self, **kwargs):
        self.ticker = kwargs.get('ticker')
        self.news_amount = kwargs.get('news_amount', 50)

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

    def get_csv(self, fname):
        if os.path.exists(fname):
            return pd.read_csv(fname, parse_dates=True, index_col=0)
        return None

    def get_json(self, fname):
        if os.path.exists(fname):
            with open(fname) as f:
                return json.load(f)
        return {}

    def get_metadata(self):
        #
        sect_fname = f"{cls.DATA_DIR}/Sectors.json"
        tags_fname = f"{cls.DATA_DIR}/Tags.json"
        #
        if not os.path.exists(sect_fname) or not os.path.exists(tags_fname):
            self.load_metadata()
        #
        sector_data = self.get_json(sect_fname)
        tags_data = self.get_json(tags_fname)
        res = {
            'sectors': [
                s['name'] for s in sector_data], 'tags': [
                t['name'] for t in tags_data]}
        return res

    def company(self):
        response = requests.get(
            f"https://cloud.iexapis.com/stable/stock/{self.ticker.lower()}/company?token={self.TOKEN}")
        response.raise_for_status()
        return response.json()

    def news(self):
        return pd.read_json(
            f"https://cloud.iexapis.com/stable/stock/{self.ticker.lower()}/news/last/{self.news_amount}?token={self.TOKEN}")

    @classmethod
    def save_data(cls, data, title):
        fname = f"{cls.DATA_DIR}/{title}.json"
        with open(fname, "w+") as f:
            json.dump(data, f, indent=4)

    def _merge_earnings(self, latest, older=None):
        if older is None:
            file_data = self.get_json(f"./IEXData/{self.ticker}.json")
            older = file_data.get('earnings', {})
        for key in latest.keys():
            if key not in older:
                older[key] = latest[key]
        return older

    def earnings(self, last=1, period='quarter', save=True, merge_only=True):
        df = pd.read_json(
            f"https://cloud.iexapis.com/stable/stock/{self.ticker.lower()}/earnings/{last}?period={period}&token={self.TOKEN}")
        latest = {v['fiscalPeriod']: v for k, v in df['earnings'].items()}
        if merge_only:
            merged = self._merge_earnings(latest)
            return merged
        if save:
            merged = self._merge_earnings(latest)
            self.save_data({'earnings': merged}, self.ticker)
            return merged
        return latest

    def crypto(self, book=False, save=True):
        if book:
            return None
        else:
            req = requests.get(
                f"https://cloud.iexapis.com/stable/crypto/{self.ticker.lower()}/quote?token={self.TOKEN}")
            print(req.json())
            df = pd.DataFrame([req.json()])
            df.drop(['symbol', 'sector', 'calculationPrice',
                    'latestSource'], 1, inplace=True)
            file_df = self.get_csv(f"./crypto/{self.ticker}_iex_quotes.csv")
            if file_df is not None:
                merged = pd.concat([df, file_df]).drop_duplicates(
                    ['latestUpdate', 'latestPrice']).reset_index(drop=True)
            else:
                merged = df
        if save:
            merged.to_csv(
                f"./crypto/{self.ticker}_iex_{'book' if book else 'quotes'}.csv")
        return merged

    @classmethod
    def load_metadata(cls):
        #
        sectors = requests.get(
            f"https://cloud.iexapis.com/stable/ref-data/sectors?token={cls.TOKEN}")
        sector_data = res.json()
        cls.save_data(sector_data, 'Sectors')
        #
        tags = requests.get(
            f"https://cloud.iexapis.com/stable/ref-data/tags?token={cls.TOKEN}")
        tags_data = res.json()
        cls.save_data(tags_data, 'Tags')
