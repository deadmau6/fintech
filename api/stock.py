import datetime as dt
import numpy as np
import pandas as pd
import yfinance as yf
import os
import glob
from scipy.stats import norm, kurtosis, skew, sem
from .decorators import requires_dataframe
from .indicators import Indicators
from .predictors import Predictors
from .options_chain import OptionsChain
from .connections import Mongo
from . import CONFIG


class Stock:

    _DB_NAME = CONFIG.DB_NAME

    def __init__(self, **kwargs):
        self._complete_dataframe = None
        self.ticker = kwargs.get('ticker')
        self.end = kwargs.get('end')
        self.start = kwargs.get('start')
        self.date_range = (self.start, self.end)
        self.folder = f"{CONFIG.DATA_LOCATION}/stocks"
        self.save = kwargs.get('save', False)
        self.localOnly = kwargs.get('localOnly', False)
        if kwargs.get('auto_load', True):
            self.load()

    @property
    def folder(self):
        return self._folder

    @folder.setter
    def folder(self, folder):
        if isinstance(folder, str) and os.path.isdir(folder):
            self._folder = os.path.abspath(folder)
        else:
            # maybe error?
            self._folder = 'stocks'

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
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        if isinstance(start, dt.datetime):
            self._start = start
        elif isinstance(start, dt.date):
            self._start = dt.datetime.fromisoformat(start.isoformat())
        elif start:
            try:
                self._start = dt.datetime.strptime(start, "%Y-%m-%d")
            except ValueError:
                raise Exception(
                    f"Start date: {start}, does not follow the format: YYYY-MM-DD.")
        else:
            self._start = dt.datetime.fromtimestamp(0)
            self._start = self.end - dt.timedelta(days=365)

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        if isinstance(end, dt.datetime):
            self._end = end
        elif isinstance(end, dt.date):
            self._end = dt.datetime.fromisoformat(end.isoformat())
        elif end:
            try:
                self._end = dt.datetime.strptime(end, "%Y-%m-%d")
            except ValueError:
                raise Exception(
                    f"End date: {end}, does not follow the format: YYYY-MM-DD.")
        else:
            self._end = dt.datetime.today()

    @property
    def dataframe(self):
        return self._dataframe

    @dataframe.setter
    def dataframe(self, data_frame):
        self._dataframe = data_frame

    @property
    def filename(self):
        # maybe validate w/ os.path?
        return f"{self.folder}/{self.ticker}_{self.website}_{self.start.date()}_{self.end.date()}.csv"

    @property
    def current(self):
        return self.dataframe.iloc[-1, ]

    @staticmethod
    def dcgr(data, column='Close'):
        """Daily Continuous Growth Rate = ln(X_t+1) - ln(X_t)"""
        ln = data.loc[:, column].apply(lambda x: np.log(x))
        dcgr = ln.diff()
        return dcgr

    @staticmethod
    def pct(data, column='Close', period=1, is_absolute=False):
        if is_absolute:
            return data.loc[:, column].pct_change(periods=period).abs()
        return data.loc[:, column].pct_change(periods=period)

    @staticmethod
    def icgr(data, open_column='Open', close_column='Close'):
        """Intra Continuous Growth Rate = ln(X_t+1) - ln(X_t)"""
        ln_close = data.loc[:, close_column].apply(lambda x: np.log(x))
        ln_open = data.loc[:, open_column].apply(lambda x: np.log(x))
        intra = ln_close - ln_open
        return intra

    @requires_dataframe
    def add_dcgr(self, column='Close', refresh=False):
        if 'DCGR' not in self._dataframe.columns or refresh:
            self._dataframe['DCGR'] = Stock.dcgr(self._dataframe, column)

    @requires_dataframe
    def add_pct(self, column='Close', period=1, refresh=False):
        pct_column = f"PCT_{column}_{period}"
        if pct_column not in self._dataframe.columns or refresh:
            self._dataframe[pct_column] = Stock.pct(
                self._dataframe, column, period)

    @requires_dataframe
    def add_icgr(
            self,
            open_column='Open',
            close_column='Close',
            refresh=False):
        if 'ICGR' not in self._dataframe.columns or refresh:
            self._dataframe['ICGR'] = Stock.icgr(
                self._dataframe, open_column, close_column)

    @requires_dataframe
    def get_dcgr(self, column='Close'):
        if 'DCGR' not in self._dataframe.columns:
            # TODO warning message maybe ask to add?
            return Stock.dcgr(self._dataframe, column)
        return self._dataframe.loc[:, 'DCGR']

    @requires_dataframe
    def get_pct(self, column='Close', period=1):
        pct_column = f"PCT_{column}_{period}"
        if pct_column not in self._dataframe.columns:
            return Stock.pct(self._dataframe, column, period)
        return self._dataframe.loc[:, pct_column]

    @requires_dataframe
    def get_icgr(self, open_column='Open', close_column='Close'):
        if 'ICGR' not in self._dataframe.columns:
            return Stock.icgr(self._dataframe, open_column, close_column)
        return self._dataframe.loc[:, 'ICGR']

    @requires_dataframe
    def get_more_stats(self, column='DCGR', remove_nans=True):
        if column not in self._dataframe.columns:
            # TODO warning message?
            raise Exception(
                f"Column {column} is missing from dataframe try one of these: {self._dataframe.columns}")
        data = self._dataframe.loc[:, column].dropna(
        ) if remove_nans else self._dataframe.loc[:, column]
        ndata = data.to_numpy()
        return {
            'mean': np.mean(ndata),
            'variance': np.var(ndata),
            'standard_deviation': np.std(ndata),
            'median': np.median(ndata),
            'max': np.max(ndata),
            'min': np.min(ndata),
            'skew': skew(ndata),
            'kurtosis': kurtosis(ndata),
            'standard_error_mean': sem(ndata)
        }

    @requires_dataframe
    def get_stats(self, column='DCGR', remove_nans=True):
        if column not in self._dataframe.columns:
            # TODO warning message?
            raise Exception(
                f"Column {column} is missing from dataframe try one of these: {self._dataframe.columns}")
        mu = self._dataframe.loc[:, column].mean(skipna=remove_nans)
        var = self._dataframe.loc[:, column].var(skipna=remove_nans)
        sigma = self._dataframe.loc[:, column].std(skipna=remove_nans)
        return {
            'mean': mu,
            'variance': var,
            'standard_deviation': sigma
        }

    @staticmethod
    def dataframe_to_records(df):
        data = df.to_dict('index')
        records = []
        for k, v in data.items():
            if isinstance(k, dt.date):
                k = dt.datetime(year=k.year, month=k.month, day=k.day)
            obj = {
                'ts': k.timestamp(),
                'year': k.year,
                'month': k.month,
                'day': k.day,
                **v}
            records.append(obj)
        return records

    @staticmethod
    def records_to_dataframe(records):
        df = pd.DataFrame(records)
        df.set_index('Date', inplace=True)
        return df

    def save_records(self):
        start = self._complete_dataframe.index[0]
        if isinstance(start, dt.datetime):
            start = start.date()
        end = self._complete_dataframe.index[-1]
        if isinstance(end, dt.datetime):
            end = end.date()
        #
        ticker = Mongo.clean_collection_name(self.ticker)
        #
        with Mongo() as client:
            if ticker not in client[self._DB_NAME].list_collection_names():
                # create collection
                client[self._DB_NAME].create_collection(ticker)
                collection = client[self._DB_NAME][ticker]
                collection.create_index([("ts", 1)])
                collection.create_index([("year", 1), ("ts", 1)])
                collection.create_index([("month", 1), ("ts", 1)])
                records = Stock.dataframe_to_records(self._complete_dataframe)
                collection.insert_many(records)
            else:
                collection = client[self._DB_NAME][ticker]
                if collection.estimated_document_count() == 0:
                    records = Stock.dataframe_to_records(
                        self._complete_dataframe)
                    collection.insert_many(records)
                else:
                    #
                    last = None
                    for record in collection.find({}, limit=1).sort('ts', -1):
                        last = dt.datetime.fromtimestamp(record['ts'])
                        last = last.date()
                    #
                    first = None
                    for record in collection.find({}, limit=1).sort('ts', 1):
                        first = dt.datetime.fromtimestamp(record['ts'])
                        first = first.date()
                    #
                    if first and start < first:
                        if end < first:
                            raise Exception(
                                f"Dates do not line up from {end} to {first}.")
                        records = Stock.dataframe_to_records(
                            self._complete_dataframe[start:first])
                        collection.insert_many(records)
                        # print(f"Added {len(records)} new prefix records")
                    if last and end > last:
                        if start > last:
                            raise Exception(
                                f"Dates do not line up from {last} to {start}.")
                        records = Stock.dataframe_to_records(
                            self._complete_dataframe[last:])
                        collection.update_one({'ts': records[0]['ts']}, {
                                              '$set': records[0]})
                        if len(records) > 1:
                            collection.insert_many(records[1:])
                        # print(f"Added {len(records)} new sufix records")

    @staticmethod
    def query(db_name, ticker, **kwargs):
        query = {}
        #
        start = kwargs.get("start")
        if start:
            query['ts'] = {'$gte': start.timestamp()}
        #
        end = kwargs.get("end")
        if end:
            if query.get("ts") is None:
                query['ts'] = {'$lte': 0}
            query['ts']['$lte'] = end.timestamp()
        #
        month = kwargs.get("month")
        if month:
            query['month'] = month
        #
        year = kwargs.get("year")
        if year:
            query['year'] = year
        #
        ticker = Mongo.clean_collection_name(ticker)
        results = []
        #
        with Mongo() as client:
            if ticker not in client[db_name].list_collection_names():
                raise Exception(f"Could not find data for ticker: {ticker}")
            collection = client[db_name][ticker]
            for rec in collection.find(query).sort('ts', 1):
                obj = {
                    'Date': dt.date(rec['year'], rec['month'], rec['day']),
                    'Open': rec['Open'],
                    'High': rec['High'],
                    'Low': rec['Low'],
                    'Close': rec['Close'],
                    'Adj Close': rec['Adj Close'],
                    'Volume': rec['Volume']
                }
                results.append(obj)
        return results

    def get_records(self):
        ticker = Mongo.clean_collection_name(self.ticker)
        #
        with Mongo() as client:
            if ticker not in client[self._DB_NAME].list_collection_names():
                return None
        records = Stock.query(
            self._DB_NAME,
            ticker,
            start=self.start,
            end=self.end)
        if len(records) == 0:
            return None
        return Stock.records_to_dataframe(records)

    def from_filename(self, filename):
        folder, fname = os.path.split(filename)
        clean_fname = fname.rstrip('.csv')
        ticker, website, start, end = clean_fname.split('_')
        #
        return folder, ticker, website, dt.datetime.strptime(
            start, "%Y-%m-%d"), dt.datetime.strptime(end, "%Y-%m-%d")

    def get_web(self, start, end):
        # print(start, end)
        try:
            return yf.download(
                self.ticker,
                start=start,
                end=end,
                progress=False,
                show_errors=False)
        except Exception as e:
            print('Error reading website')
            print(e)
            return None

    def get_csv(self, fname):
        if os.path.exists(fname):
            return pd.read_csv(fname, parse_dates=True, index_col=0)
        return None

    def save_csv(self):
        if os.path.exists(self.filename):
            return None
        print(f"saved file: {self.filename}")
        self._complete_dataframe.to_csv(self.filename)

    def find_nearest_csv(self):
        with os.scandir(f"{self.folder}") as d:
            for entry in d:
                if entry.name.startswith(
                        f"{self.ticker}_{self.website}") and entry.is_file():
                    return f"{self.folder}/{entry.name}"
        return None

    def _get_data(self):
        # dataframe = self.get_csv(self.filename)
        dataframe = self.get_records()
        if dataframe is None:
            return self.get_web(self.start, self.end)
        # near_file = self.find_nearest_csv()
        # if near_file:
        #     folder, ticker, website, start, end = self.from_filename(near_file)
        #     dataframe = self.get_csv(near_file)
        #     changes = False
        #     pre = None
        #     if start > self.start:
        #         pre = self.get_web(ticker, website, self.start, start)
        #         changes = True
        #     else:
        #         self.start = f"{start.date()}"
        #     post = None
        #     if end < self.end:
        #         post = self.get_web(ticker, website, end, self.end)
        #         changes = True
        #     else:
        #         self.end = f"{end.date()}"
        #     if changes:
        #         if self.save:
        #             os.remove(near_file)
        #         return pd.concat([pre, dataframe, post]).reset_index().drop_duplicates('Date').set_index('Date')
        #     else:
        #         return dataframe
        # return self.get_web(self.ticker, self.website, self.start, self.end)
        start = dataframe.index[0]
        end = dataframe.index[-1]
        changes = False
        pre = None
        if start > self.start.date():
            pre = self.get_web(self.start, start)
            changes = True
        else:
            self.start = f"{start.date() if isinstance(start, dt.datetime) else start}"
        post = None
        if end < self.end.date():
            post = self.get_web(end, self.end.date())
            changes = True
        else:
            self.end = f"{end.date() if isinstance(end, dt.datetime) else end}"
        if changes:
            return pd.concat([pre, dataframe, post]).reset_index(
            ).drop_duplicates('Date').set_index('Date')
        return dataframe

    def load(self):
        if self.localOnly:
            self._complete_dataframe = self.get_records()
            if self._complete_dataframe is None:
                raise Exception(
                    f"Could not find local data for {self.ticker}.")
            # near_file = self.find_nearest_csv()
            # if near_file is None:
            #     raise Exception(f"Could not find local data for {self.ticker}.")
            # self._complete_dataframe = self.get_csv(near_file)
            # if self._complete_dataframe is None:
            #     raise Exception(f"Could not load local data for {self.ticker} at {near_file}.")
            start = self._complete_dataframe.index[0]
            end = self._complete_dataframe.index[-1]
            self.dataframe = self._complete_dataframe
            if start < self.start and self.start < end:
                self.dataframe = self.dataframe[f"{self.start.date()}":]
            if end > self.end and self.end > start:
                self.dataframe = self.dataframe[:f"{self.end.date()}"]
        else:
            self._complete_dataframe = self._get_data()
            if self.save:
                self.save_records()
            self.dataframe = self._complete_dataframe[self.date_range[0].date(
            ):self.date_range[1].date()]
            # self.dataframe = self._complete_dataframe[f"{self.date_range[0].date()}":f"{self.date_range[1].date()}"]

    def percentage_change(self, hm_days=7):
        df = self.dataframe[-1 * hm_days - 1:][::-1].copy()
        df.drop(['High', 'Low', 'Open', 'Close', 'Volume'], 1, inplace=True)
        today = df['Adj Close'][0]
        direction = []
        percent = []
        for i in range(hm_days + 1):
            diff = today - df['Adj Close'][i]
            direction.append('+' if diff >= 0 else '-')
            percent.append((abs(diff) / df['Adj Close'][i]) * 100)
        df['Direction'] = direction
        df['Percent'] = percent
        return df

    def get_indicator(self, indicator_name, **kwargs):
        if indicator_name not in Indicators.available_indicators:
            raise NotImplementedError(
                f'Strategy {indicator_name} not implemented')
        indicator = getattr(Indicators, indicator_name)
        if indicator:
            return indicator(self.dataframe, **kwargs)

    def get_prediction(self, prediction_name, **kwargs):
        if prediction_name not in Predictors.available:
            raise NotImplementedError(
                f'Predictor {prediction_name} not implemented')
        prediction = getattr(Predictors, prediction_name)
        if prediction:
            return prediction(self.dataframe, **kwargs)

    def get_options_data(self):
        return OptionsChain(self.ticker)
