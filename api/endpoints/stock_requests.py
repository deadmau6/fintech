from math import ceil
from typing import Optional
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Path, Query, HTTPException
#
from .request_models import StockTicker, ZeroShotParams, TickersList
from ..static import IEX_SECTORS, IEX_ISSUE_TYPES
from ..company import Company
from ..stock import Stock
from ..utils import Utils
#
import json
from os import path

router = APIRouter()

@router.get("/stock/{ticker}/")
async def query_stock_data(
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID."),
    start: Optional[str] = Query(None, regex=r"\d{4}-\d{2}-\d{2}", title="Start Date", description="The starting day in YYYY-MM-DD format."),
    end: Optional[str] = Query(None, regex=r"\d{4}-\d{2}-\d{2}", title="End Date", description="The ening day in YYYY-MM-DD format."),
    website: Optional[str] = Query("yahoo", title="Website", description="Which website to pull stock data from."),
    save: Optional[bool] = Query(True, title="Save", description="Update and save the results on local disk.")
    ):
    """ Query stock data and returned in Pandas freindly format."""
    fin = Stock(ticker=ticker, start=start, end=end, website=website, save=save, auto_load=False)
    # try block ?
    fin.load()
    result = fin.dataframe.to_dict()
    return result

#TODO: /stock/info/company_or_ticker
@router.get("/stock/symbols")
async def get_comapny_symbols(
    page: Optional[int] = Query(0, gte=0, title="Page Number", description="The page number to collect symbols from."),
    limit: Optional[int] = Query(25, ge=10, le=100, title="Page Limit", description="The number of results to retrieve at a time."),
    issueType: Optional[str] = Query(None, title="Issue Type", description=f"The type of the stock. Must be one of the following: {IEX_ISSUE_TYPES}."),
    sector: Optional[str] = Query(None, title="Sector", description=f"The sector of the stock. Must be one of the following: {IEX_SECTORS}.")):
    """This function only gets company symbols that have company info available."""
    skip = page * limit
    response = Company().get_symbols(skip, limit, issueType, sector)
    response['page'] = page
    response['pages'] = [i for i in range(ceil(response['total'] / limit))]
    return response

#TODO: /stock/info/company_or_ticker
@router.post("/stock/info/")
async def get_company_info(data: TickersList):
    response = {}
    for tick in data.tickers:
        response[tick.upper()] = Company().get_by_symbol(tick)
    return response

@router.get("/stock/options/test")
async def get_options_chain_temp():
    fpath = path.abspath("/home/joe/Downloads/options_chain_reponse_test.json")
    with open(fpath, "r") as f:
        response = json.load(f)
    return response

@router.get("/stock/options/{ticker}")
async def get_options_chain(
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID."),
    start: Optional[str] = Query(None, regex=r"\d{4}-\d{2}-\d{2}", title="Start Date", description="The starting day in YYYY-MM-DD format."),
    end: Optional[str] = Query(None, regex=r"\d{4}-\d{2}-\d{2}", title="End Date", description="The ening day in YYYY-MM-DD format."),
    website: Optional[str] = Query("yahoo", title="Website", description="Which website to pull stock data from."),
    save: Optional[bool] = Query(True, title="Save", description="Update and save the results on local disk."),
    dateString: Optional[str] = Query(None, regex=r"\d{4}-\d{2}-\d{2}", title="Options Date", description="The Options date in YYYY-MM-DD format."),
    drift: Optional[float] = Query(None, title="Drift", description="The mean of the daily growth rate of the stock prices. (None means it will be calculated)"),
    volatillity: Optional[float] = Query(None, title="Volatillity", description="The Standard Deviation of the daily growth rate of the stock prices. (None means it will be calculated)"),
    rfir: Optional[float] = Query(0.001, title="Risk Free Interest Rate", description="The Risk Free Interest Rate, it is mostly static and can be near zero. (default 0.001)")):
    """This function gets the option chain for the given date and ticker, the default date used is the first available option date"""
    fin = Stock(ticker=ticker, start=start, end=end, website=website, save=save, auto_load=False)
    if start is None:
        fin.start = fin.end - timedelta(days=365)
    # try block ? cache?
    fin.load()
    if drift is None and volatillity is None:
        dcgr = fin.get_dcgr()
        drift = dcgr.mean(skipna=True)
        volatillity = dcgr.std(skipna=True)
    #
    current = fin.dataframe.iloc[-1, ]
    current_price = current['Close']
    #
    options = fin.get_options_data()
    #
    dates = {}
    today = date.today()
    for date_str in options.dates:
        td = date.fromisoformat(date_str) - today
        days = td.days
        dates[date_str] = days
    date_string = dateString if dateString else options.dates[0]
    #
    calls, puts = options.extended_options_chain(date_string, current_price, drift, volatillity, dates[date_string], rfir)
    #
    calls = calls.round(4)
    calls.fillna('', inplace=True)
    calls = json.loads(json.dumps(calls.to_dict('records'), default=Utils.convert_numpy_types))
    #
    puts = puts.round(4)
    puts.fillna('', inplace=True)
    puts = json.loads(json.dumps(puts.to_dict('records'), default=Utils.convert_numpy_types))
    #
    return {"dateString": date_string, "dates": dates, "calls": calls, "puts": puts}