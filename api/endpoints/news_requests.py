from typing import List, Optional
from fastapi import APIRouter, Body, Path, Query, HTTPException, BackgroundTasks
from ..news import News
from .request_models import StockTicker, ZeroShotParams, TickersList
from pprint import pprint

router = APIRouter()

@router.get('/news/saved')
async def get_stocks_on_disk():
    """ Returns list of stock tickers that are currently saved saved on disk with news data."""
    return News().get_saved_stocks()

@router.get('/news/sentiment/functions')
async def get_sentiment_functions():
    """ Returns a list of sentiment analysis functions that are available to be executed."""
    return {"available": list(News._SENTIMENT.keys())}

@router.post('/news/coherence')
async def get_coherence_state(data: TickersList):
    """ This will return the current Coherence State.
    The Coherence state is just a count of various records for the given stock.
    {
        stock: The stock ticker.
        total_records: The total number of raw news data stored.
        metrics_records: The number of metrics entries for the stock.
        sentiment_records: Each sentiment function and its record count in Metrics.
    }
    """
    results = {}
    for tick in data.tickers:
        coher = News().get_coherence_state(tick.upper())
        results[tick.upper()] = {
            'total_records': coher['total_records'],
            'metrics_records': coher['metrics_records'],
            'sentiment_records': coher['sentiment_records']}
    return results

@router.post('/news/iex/update')
async def update_single_stock(data: StockTicker):
    """ This will save and return more news data from iex for a single stock.""" 
    news = News().iex_update_single_stock(data.ticker.upper())
    return {'inserted': news['inserted'], 'total_data': news['data'].to_dict("records")}

@router.post('/news/iex/batched')
async def update_iex_batch(data: TickersList, background_tasks: BackgroundTasks):
    """ This will save more news data from iex for a list of stocks.""" 
    news = News()
    background_tasks.add_task(news.iex_update_batch, data.tickers)
    return {'message': 'background task started'}

@router.post('/news/metrics/update')
async def update_metrics(data: TickersList):
    """ This updates the Metrics store with the latest data for a list of stocks."""
    results = {}
    for tick in data.tickers:
        results[tick.upper()] = News().update_metrics(tick.upper())
    return results

@router.post('/news/sentiment/{ticker}/zero-shot')
async def update_zeroshot_sentiment(
    data: ZeroShotParams,
    background_tasks: BackgroundTasks,
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID.")):
    #
    # TODO: THIS NEEDS TO BE A BACKGROUND TASK.
    #
    stock = ticker.upper()
    missing_ids = News().get_missing_metric_function(stock, 'zero-shot', data.key_names, lang=data.lang, limit=data.limit)
    # TODO if len(missing_ids) == 0
    if len(missing_ids) == 0:
        return { 'count_processing': 0, 'message': "No new updates."}
    missing_data = News().get_raw_stock_data(stock, {'_id': {'$in': missing_ids} }, {k: 1 for k in data.key_names})    
    news = News()
    background_tasks.add_task(news.task_update_zero_shot, stock, missing_data, data.lang, data.key_names, data.canidate_labels)
    return { 'count_processing': len(missing_ids) }
