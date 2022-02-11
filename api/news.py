from datetime import datetime
from pprint import pprint
from pymongo import UpdateOne
#
from .sentiment import Sentiment
from .connections import Mongo
from .iex import IEX


class News:

    _DB_NAME = 'news'
    _METRICS = 'Metrics'
    _SENTIMENT = {'zero-shot': ['headline', 'summary']}

    @staticmethod
    def format_key_name(function_name, data_field_name):
        return f"{function_name}-{data_field_name}-results"

    @classmethod
    def get_saved_stocks(cls):
        with Mongo() as client:
            results = [
                x for x in client[cls._DB_NAME].list_collection_names() if x != cls._METRICS]
        return {'available_stocks': results}

    @classmethod
    def get_foriegn_keys(cls, stock):
        #
        with Mongo() as client:
            collection = client[cls._DB_NAME][cls._METRICS]
            results = [x['foriegn_key'] for x in collection.find(
                {'stock': stock}, {'foriegn_key': 1})]
        #
        return results

    @classmethod
    def get_stock_ids(cls, stock):
        #
        with Mongo() as client:
            #
            if stock not in client[cls._DB_NAME].list_collection_names():
                raise Exception(f'{stock} Collection not found')
            #
            collection = client[cls._DB_NAME][stock]
            results = [x['_id'] for x in collection.find({}, {'_id': 1})]
        #
        return results

    @classmethod
    def get_missing_ids(cls, stock):
        #
        original_ids = set(cls.get_stock_ids(stock))
        metric_ids = set(cls.get_foriegn_keys(stock))
        #
        return original_ids - metric_ids

    @classmethod
    def get_raw_stock_data(cls, stock, query={}, proj=None):
        #
        with Mongo() as client:
            #
            if stock not in client[cls._DB_NAME].list_collection_names():
                raise Exception(f'{stock} Collection not found')
            #
            collection = client[cls._DB_NAME][stock]
            results = [x for x in collection.find(query, proj)]
        #
        return results

    @classmethod
    def get_stock_metrics_data(cls, stock, query={}, proj=None, kwargs={}):
        filt = query
        filt['stock'] = stock
        #
        with Mongo() as client:
            #
            if stock not in client[cls._DB_NAME].list_collection_names():
                raise Exception(f'{stock} Collection not found')
            #
            collection = client[cls._DB_NAME][cls._METRICS]
            results = [
                x for x in collection.find(
                    filt,
                    projection=proj,
                    **kwargs)]
        #
        return results

    @classmethod
    def get_missing_metric_function(
            cls,
            stock,
            function_name,
            fields,
            limit=0,
            lang=None):
        ids = []
        #
        with Mongo() as client:
            if stock not in client[cls._DB_NAME].list_collection_names():
                raise Exception(f'{stock} Collection not found')
            #
            metrics = client[cls._DB_NAME][cls._METRICS]
            for field in fields:
                key = News.format_key_name(function_name, field)
                if lang is None:
                    query = metrics.find({'stock': stock, key: {'$exists': False}}, {
                                         'foriegn_key': 1}, limit=limit)
                else:
                    query = metrics.find({'stock': stock, 'lang': lang, key: {'$exists': False}}, {
                                         'foriegn_key': 1}, limit=limit)
                for q in query:
                    if q['foriegn_key'] not in ids:
                        ids.append(q['foriegn_key'])
        #
        return ids

    @classmethod
    def count_records(cls, stock):
        #
        orig = 0
        metric = 0
        #
        with Mongo() as client:
            if stock not in client[cls._DB_NAME].list_collection_names():
                raise Exception(f'{stock} Collection not found')
            #
            orig = client[cls._DB_NAME][stock].count_documents({})
            metric = client[cls._DB_NAME][cls._METRICS].count_documents({
                                                                        'stock': stock})
        #
        return {'stock_count': orig, 'metrics_count': metric}

    @classmethod
    def count_metric_functions(cls, stock, function_name, fields):
        count = {}
        #
        with Mongo() as client:
            if stock not in client[cls._DB_NAME].list_collection_names():
                raise Exception(f'{stock} Collection not found')
            #
            for field in fields:
                key = News.format_key_name(function_name, field)
                count[field] = client[cls._DB_NAME][cls._METRICS].count_documents(
                    {'stock': stock, key: {'$exists': True}})
        #
        return count

    @classmethod
    def get_coherence_state(cls, stock):
        #
        records = cls.count_records(stock)
        sentiment_counts = {}
        #
        for fname, fields in cls._SENTIMENT.items():
            sentiment_counts[fname] = cls.count_metric_functions(
                stock, fname, fields)
        #
        return {
            'stock': stock,
            'total_records': records['stock_count'],
            'metrics_records': records['metrics_count'],
            'sentiment_records': sentiment_counts
        }

    @classmethod
    def update_metrics(cls, stock):
        #
        diff = list(cls.get_missing_ids(stock))
        if len(diff) == 0:
            # print something?
            return {
                'inserted': 0,
                'message': "No new records. Update completed."}
        projection = {'_id': 1, 'source': 1, 'lang': 1, 'datetime': 1}
        #
        unique_map = [
            (stock, 'stock'),
            ('_id', 'foriegn_key'),
            ('source', 'source'),
            ('lang', 'lang'),
            ('datetime', 'datetime')]
        inserted_count = 0
        #
        with Mongo() as client:
            #
            missing_query = client[cls._DB_NAME][stock].find(
                {'_id': {'$in': diff}}, projection)
            #
            # a little messy, don't ya think?
            missing = [{key: item[val] if key != 'stock' else val for val,
                        key in unique_map} for item in missing_query]
            #
            results = client[cls._DB_NAME][cls._METRICS].insert_many(missing)
            #
            inserted_count = len(results.inserted_ids)
        return {'inserted': inserted_count, 'message': "Update completed."}

    @staticmethod
    def _iex_clean_news(news_df):
        #
        # unique_key = datetime + headline + source + lang
        news_df.drop_duplicates(
            subset=[
                'datetime',
                'headline',
                'source',
                'lang',
                'summary'],
            inplace=True)
        # news_df.set_index('dt', inplace=True)
        #
        # important fields = [datetime,headline,source,summary,related,lang]
        current_cols = set(news_df.columns)
        important_fields = set(
            ['datetime', 'headline', 'source', 'lang', 'summary', 'related'])
        diff = current_cols - important_fields
        #
        news_df.drop(diff, axis=1, inplace=True)
        #
        cleaned = [{**x, 'datetime': x['datetime'].to_pydatetime()}
                   for x in news_df.to_dict('records')]
        return cleaned

    @classmethod
    def save_news(cls, ticker, ndf):
        inserted_count = 0
        #
        with Mongo() as client:
            news_db = client[cls._DB_NAME]
            if ticker not in news_db.list_collection_names():
                # create collection
                news_db.create_collection(
                    ticker, storageEngine={
                        'wiredTiger': {
                            'configString': "block_compressor=zstd"}})
                collection = news_db[ticker]
                result = collection.insert_many(ndf)
                inserted_count = len(result.inserted_ids)
            else:
                collection = news_db[ticker]
                for x in ndf:
                    exists = collection.find_one(
                        {
                            'datetime': x['datetime'],
                            'headline': x['headline'],
                            'source': x['source'],
                            'lang': x['lang']})
                    if exists is None:
                        result = collection.insert_one(x)
                        inserted_count += 1
        return inserted_count

    @classmethod
    def iex_update_single_stock(cls, stock):
        stock = stock.upper()
        iex = IEX(ticker=stock)
        ndf = iex.news()
        cleaned_ndf = News._iex_clean_news(ndf)
        count = cls.save_news(stock, cleaned_ndf)
        return {'inserted': count, 'data': ndf}

    @classmethod
    def iex_update_batch(cls, stocks):
        results = {}
        for stock in stocks:
            data = cls.iex_update_single_stock(stock.upper())
            results[stock.upper()] = data['inserted']
        # ToDo: properly log results
        print(results)
        print('\nCompleted\n')

    @classmethod
    def task_update_zero_shot(cls, stock, data, lang, fields, canidate_labels):
        sent_results = Sentiment.zero_shot_classification(
            data, lang=lang, fields=fields, canidate_labels=canidate_labels)
        sent_writes = []
        #
        for entry in sent_results:
            #
            filt = {'stock': stock, 'lang': lang}
            update = {}
            #
            for k, v in entry.items():
                if k == '_id':
                    filt['foriegn_key'] = v
                elif k not in fields:
                    update[k] = v
            #
            sent_writes.append(UpdateOne(filt, {'$set': update}))
        with Mongo() as client:
            inserted = client[cls._DB_NAME][cls._METRICS].bulk_write(
                sent_writes)
        # ToDo: properly log results
        print('\nCompleted\n')
