from typing import Optional
from fastapi import APIRouter, Path, Query, HTTPException
from ..stock import Stock
from .request_models import StockTicker, Defaults
from ..utils import Utils
from pprint import pprint
import json

router = APIRouter()

@router.get('/predictor/svr/{ticker}/')
async def get_svr(
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID."),
    start: Optional[str] = Query(Defaults.START_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="Start Date", description="The starting day in YYYY-MM-DD format."),
    end: Optional[str] = Query(Defaults.END_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="End Date", description="The ening day in YYYY-MM-DD format."),
    website: Optional[str] = Query("yahoo", title="Website", description="Which website to pull stock data from."),
    save: Optional[bool] = Query(True, title="Save", description="Update and save the results on local disk."),
    column: Optional[str] = Query("Adj Close", title="Dataframe Column", description="Which dataframe column to perform the calculations on."),
    prev: Optional[int] = Query(15, title="Previous Days", description=".", gt=0),
    buff: Optional[int] = Query(3, title="Buffer Days", description=".", gt=0),
    lookahead: Optional[int] = Query(3, title="Lookahead Days", description=".", gt=0)
    ):
    """ Quickly runs the given indicator for the stock with only its default parameters.
    column='Adj Close', prev_days=15, buff_days=3, lookahead_days=3"""
    fin = Stock(ticker=ticker, start=start, end=end, website=website, save=save, auto_load=False)
    # try block ?
    fin.load()
    results = fin.get_prediction('svr', column=column, prev_days=prev, buff_days=buff, lookahead_days=lookahead)
    #
    return json.loads(json.dumps(results, default=Utils.convert_numpy_types))

@router.get('/predictor/decision_tree/{ticker}/')
async def get_decision_tree(
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID."),
    start: Optional[str] = Query(Defaults.START_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="Start Date", description="The starting day in YYYY-MM-DD format."),
    end: Optional[str] = Query(Defaults.END_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="End Date", description="The ening day in YYYY-MM-DD format."),
    website: Optional[str] = Query("yahoo", title="Website", description="Which website to pull stock data from."),
    save: Optional[bool] = Query(True, title="Save", description="Update and save the results on local disk."),
    column: Optional[str] = Query("Adj Close", title="Dataframe Column", description="Which dataframe column to perform the calculations on."),
    future: Optional[int] = Query(25, title="Future Days", description=".", gt=0)
    ):
    """ Quickly runs the given indicator for the stock with only its default parameters.
    column='Adj Close', prev_days=15, buff_days=3, lookahead_days=3"""
    fin = Stock(ticker=ticker, start=start, end=end, website=website, save=save, auto_load=False)
    # try block ?
    fin.load()
    results = fin.get_prediction('decision_tree', column=column, future_days=future)
    #
    return json.loads(json.dumps(results, default=Utils.convert_numpy_types))

@router.get('/predictor/linear_regression/{ticker}/')
async def get_linear_regression(
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID."),
    start: Optional[str] = Query(Defaults.START_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="Start Date", description="The starting day in YYYY-MM-DD format."),
    end: Optional[str] = Query(Defaults.END_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="End Date", description="The ening day in YYYY-MM-DD format."),
    website: Optional[str] = Query("yahoo", title="Website", description="Which website to pull stock data from."),
    save: Optional[bool] = Query(True, title="Save", description="Update and save the results on local disk."),
    column: Optional[str] = Query("Adj Close", title="Dataframe Column", description="Which dataframe column to perform the calculations on."),
    future: Optional[int] = Query(25, title="Future Days", description=".", gt=0)
    ):
    """ Quickly runs the given indicator for the stock with only its default parameters.
    column='Adj Close', prev_days=15, buff_days=3, lookahead_days=3"""
    fin = Stock(ticker=ticker, start=start, end=end, website=website, save=save, auto_load=False)
    # try block ?
    fin.load()
    results = fin.get_prediction('linear_regression', column=column, future_days=future)
    #
    return json.loads(json.dumps(results, default=Utils.convert_numpy_types))
