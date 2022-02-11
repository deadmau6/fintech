from typing import Optional
from fastapi import APIRouter, Body, Path, Query, HTTPException
from .request_models import StockTicker, Defaults
from ..stock import Stock 
from ..indicators import Indicators
from ..utils import Utils
import json

router = APIRouter()

@router.get('/indicator/available')
async def get_stocks_on_disk():
    """ Returns list of available indicators."""
    return Indicators.available_indicators

@router.get('/indicator/info/{indicator}')
async def get_indicator_info(indicator: str = Path(..., title="Indicator", description="A valid indicator function."),):
    """ Returns list of available indicators."""
    if indicator not in Indicators.available_indicators:
            raise NotImplementedError(f'Strategy {indicator} not implemented')
    strategy = getattr(Indicators, indicator)
    return { 'info': strategy.__doc__ }

@router.get('/indicator/obv/{ticker}/')
async def get_obv(
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID."),
    start: Optional[str] = Query(Defaults.START_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="Start Date", description="The starting day in YYYY-MM-DD format."),
    end: Optional[str] = Query(Defaults.END_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="End Date", description="The ening day in YYYY-MM-DD format."),
    website: Optional[str] = Query("yahoo", title="Website", description="Which website to pull stock data from."),
    save: Optional[bool] = Query(True, title="Save", description="Update and save the results on local disk."),
    column: Optional[str] = Query("Close", title="Dataframe Column", description="Which dataframe column to perform the calculations on."),
    period: Optional[int] = Query(20, title="EMA Period", description="The Exponential Mean Average Period for the OBV.", gt=0)
    ):
    """ Quickly runs the given indicator for the stock with only its default parameters."""
    fin = Stock(ticker=ticker, start=start, end=end, website=website, save=save, auto_load=False)
    # try block ?
    fin.load()
    results = fin.get_indicator('obv', column=column, period=period)
    #
    # {'Buy': sig_buy, 'Sell': sig_sell, 'OBV': obv, 'OBV_EMA': obv_ema, 'Earnings': earnings}
    #
    cleaned = {}
    cleaned['OBV'] = results['OBV']
    cleaned['Buy'] = Utils.remove_nulls(results['Buy'], index=fin.dataframe.index)
    cleaned['Sell'] = Utils.remove_nulls(results['Sell'], index=fin.dataframe.index)
    cleaned['OBV_EMA'] = results['OBV_EMA'].to_dict()
    cleaned['Earnings'] = [(ts.isoformat(), val) for ts, val in results['Earnings']]
    #
    return json.loads(json.dumps(cleaned, default=Utils.convert_numpy_types))

@router.get('/indicator/rsi/{ticker}/')
async def get_rsi(
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID."),
    start: Optional[str] = Query(Defaults.START_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="Start Date", description="The starting day in YYYY-MM-DD format."),
    end: Optional[str] = Query(Defaults.END_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="End Date", description="The ening day in YYYY-MM-DD format."),
    website: Optional[str] = Query("yahoo", title="Website", description="Which website to pull stock data from."),
    save: Optional[bool] = Query(True, title="Save", description="Update and save the results on local disk."),
    column: Optional[str] = Query("Close", title="Dataframe Column", description="Which dataframe column to perform the calculations on."),
    period: Optional[int] = Query(14, title="Period", description="The Period for the RSI.", gt=0)
    ):
    """ Quickly runs the given indicator for the stock with only its default parameters."""
    fin = Stock(ticker=ticker, start=start, end=end, website=website, save=save, auto_load=False)
    # try block ?
    fin.load()
    results = fin.get_indicator('rsi', column=column, period=period)
    #
    # {'RSI': rsi}
    #
    cleaned = {}
    rsi = results['RSI']
    rsi.dropna(inplace=True)
    res_rsi = rsi.to_dict()
    cleaned['RSI'] = { ts.isoformat(): val for ts, val in res_rsi.items() }
    #
    return json.loads(json.dumps(cleaned, default=Utils.convert_numpy_types))

@router.get('/indicator/money_flow_index/{ticker}/')
async def get_money_flow_index(
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID."),
    start: Optional[str] = Query(Defaults.START_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="Start Date", description="The starting day in YYYY-MM-DD format."),
    end: Optional[str] = Query(Defaults.END_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="End Date", description="The ening day in YYYY-MM-DD format."),
    website: Optional[str] = Query("yahoo", title="Website", description="Which website to pull stock data from."),
    save: Optional[bool] = Query(True, title="Save", description="Update and save the results on local disk."),
    column: Optional[str] = Query("Close", title="Dataframe Column", description="Which dataframe column to perform the calculations on."),
    period: Optional[int] = Query(14, title="Period", description="The Period for the MFI.", gt=0),
    high: Optional[int] = Query(80, title="High", description="", gt=0),
    low: Optional[int] = Query(20, title="Low", description="", gt=0)
    ):
    """ Quickly runs the given indicator for the stock with only its default parameters."""
    fin = Stock(ticker=ticker, start=start, end=end, website=website, save=save, auto_load=False)
    # try block ?
    fin.load()
    results = fin.get_indicator('money_flow_index', column=column, period=period, high=high, low=low)
    #
    # {'Buy': buy_signal, 'Sell': sell_signal, 'MFI': mfi, 'High': high, 'Low': low, 'Period': period, 'Earnings': earnings}
    #
    cleaned = {}
    cleaned['Buy'] = Utils.remove_nulls(results['Buy'], index=fin.dataframe.index)
    cleaned['Sell'] = Utils.remove_nulls(results['Sell'], index=fin.dataframe.index)
    cleaned['MFI'] = results['MFI']
    cleaned['High'] = results['High']
    cleaned['Low'] = results['Low']
    cleaned['Period'] = results['Period']
    cleaned['Earnings'] = [(ts.isoformat(), val) for ts, val in results['Earnings']]
    #
    return json.loads(json.dumps(cleaned, default=Utils.convert_numpy_types))

@router.get('/indicator/macd/{ticker}/')
async def get_macd(
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID."),
    start: Optional[str] = Query(Defaults.START_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="Start Date", description="The starting day in YYYY-MM-DD format."),
    end: Optional[str] = Query(Defaults.END_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="End Date", description="The ening day in YYYY-MM-DD format."),
    website: Optional[str] = Query("yahoo", title="Website", description="Which website to pull stock data from."),
    save: Optional[bool] = Query(True, title="Save", description="Update and save the results on local disk."),
    column: Optional[str] = Query("Close", title="Dataframe Column", description="Which dataframe column to perform the calculations on."),
    shortPeriod: Optional[int] = Query(12, title="Short Period", description="The Period for the MFI.", gt=0),
    longPeriod: Optional[int] = Query(26, title="Long Period", description="", gt=0),
    signalPeriod: Optional[int] = Query(9, title="Signal Period", description="", gt=0)
    ):
    """ Quickly runs the given indicator for the stock with only its default parameters."""
    fin = Stock(ticker=ticker, start=start, end=end, website=website, save=save, auto_load=False)
    # try block ?
    fin.load()
    results = fin.get_indicator('macd', column=column, short_period=shortPeriod, long_period=longPeriod, signal_period=signalPeriod)
    #
    # {'MACD': macd, 'Signal': signal}
    #
    results['MACD'] = results['MACD'].to_dict()
    results['Signal'] = results['Signal'].to_dict()
    cleaned = {}
    cleaned['MACD'] = { ts.isoformat(): val for ts, val  in results['MACD'].items()}
    cleaned['Signal'] = { ts.isoformat(): val for ts, val  in results['Signal'].items()}
    #
    return json.loads(json.dumps(cleaned, default=Utils.convert_numpy_types))

@router.get('/indicator/macd_crossover/{ticker}/')
async def get_macd_crossover(
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID."),
    start: Optional[str] = Query(Defaults.START_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="Start Date", description="The starting day in YYYY-MM-DD format."),
    end: Optional[str] = Query(Defaults.END_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="End Date", description="The ening day in YYYY-MM-DD format."),
    website: Optional[str] = Query("yahoo", title="Website", description="Which website to pull stock data from."),
    save: Optional[bool] = Query(True, title="Save", description="Update and save the results on local disk."),
    column: Optional[str] = Query("Close", title="Dataframe Column", description="Which dataframe column to perform the calculations on."),
    shortPeriod: Optional[int] = Query(12, title="Short Period", description="The Period for the MFI.", gt=0),
    longPeriod: Optional[int] = Query(26, title="Long Period", description="", gt=0),
    signalPeriod: Optional[int] = Query(9, title="Signal Period", description="", gt=0)
    ):
    """ Quickly runs the given indicator for the stock with only its default parameters."""
    fin = Stock(ticker=ticker, start=start, end=end, website=website, save=save, auto_load=False)
    # try block ?
    fin.load()
    results = fin.get_indicator('macd_crossover', column=column, short_period=shortPeriod, long_period=longPeriod, signal_period=signalPeriod)
    #
    # {'Buy': sig_buy, 'Sell': sig_sell, 'MACD': macd, 'Signal': signal, 'Earnings': earnings}
    #
    results['MACD'] = results['MACD'].to_dict()
    results['Signal'] = results['Signal'].to_dict()
    cleaned = {}
    cleaned['MACD'] = { ts.isoformat(): val for ts, val  in results['MACD'].items()}
    cleaned['Signal'] = { ts.isoformat(): val for ts, val  in results['Signal'].items()}
    cleaned['Buy'] = Utils.remove_nulls(results['Buy'], index=fin.dataframe.index)
    cleaned['Sell'] = Utils.remove_nulls(results['Sell'], index=fin.dataframe.index)
    cleaned['Earnings'] = [(ts.isoformat(), val) for ts, val in results['Earnings']]
    #
    return json.loads(json.dumps(cleaned, default=Utils.convert_numpy_types))

@router.get('/indicator/bollinger_bands/{ticker}/')
async def get_bollinger_bands(
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID."),
    start: Optional[str] = Query(Defaults.START_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="Start Date", description="The starting day in YYYY-MM-DD format."),
    end: Optional[str] = Query(Defaults.END_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="End Date", description="The ening day in YYYY-MM-DD format."),
    website: Optional[str] = Query("yahoo", title="Website", description="Which website to pull stock data from."),
    save: Optional[bool] = Query(True, title="Save", description="Update and save the results on local disk."),
    column: Optional[str] = Query("Close", title="Dataframe Column", description="Which dataframe column to perform the calculations on."),
    period: Optional[int] = Query(20, title="EMA Period", description="The Exponential Mean Average Period for the bollinger_bands.", gt=0)
    ):
    """ Quickly runs the given indicator for the stock with only its default parameters."""
    fin = Stock(ticker=ticker, start=start, end=end, website=website, save=save, auto_load=False)
    # try block ?
    fin.load()
    results = fin.get_indicator('bollinger_bands', column=column, period=period)
    #
    # { 'Buy': sig_buy, 'Sell': sig_sell, 'UpperBand': upper_band, 'LowerBand': lower_band, 'SMA': sma, 'STD': std, 'Period': period, 'Earnings': earnings}  
    #
    results['LowerBand'].dropna(inplace=True)
    results['UpperBand'].dropna(inplace=True)
    results['SMA'].dropna(inplace=True)
    results['STD'].dropna(inplace=True)
    #
    lower_band = results['LowerBand'].to_dict()
    upper_band = results['UpperBand'].to_dict()
    sma = results['SMA'].to_dict()
    std = results['STD'].to_dict()
    #
    cleaned = {}
    cleaned['Buy'] = Utils.remove_nulls(results['Buy'], index=fin.dataframe.index)
    cleaned['Sell'] = Utils.remove_nulls(results['Sell'], index=fin.dataframe.index)
    cleaned['UpperBand'] = { ts.isoformat(): val for ts, val  in upper_band.items()}
    cleaned['LowerBand'] = { ts.isoformat(): val for ts, val  in lower_band.items()}
    cleaned['SMA'] = { ts.isoformat(): val for ts, val  in sma.items()}
    cleaned['STD'] = { ts.isoformat(): val for ts, val  in std.items()}
    cleaned['Period'] = results['Period']
    cleaned['Earnings'] = [(ts.isoformat(), val) for ts, val in results['Earnings']]
    #
    return json.loads(json.dumps(cleaned, default=Utils.convert_numpy_types))

@router.get('/indicator/dual_moving_average/{ticker}/')
async def get_dual_moving_average(
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID."),
    start: Optional[str] = Query(Defaults.START_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="Start Date", description="The starting day in YYYY-MM-DD format."),
    end: Optional[str] = Query(Defaults.END_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="End Date", description="The ening day in YYYY-MM-DD format."),
    website: Optional[str] = Query("yahoo", title="Website", description="Which website to pull stock data from."),
    save: Optional[bool] = Query(True, title="Save", description="Update and save the results on local disk."),
    column: Optional[str] = Query("Close", title="Dataframe Column", description="Which dataframe column to perform the calculations on."),
    shortPeriod: Optional[int] = Query(30, title="Short Period", description="The Period for the MFI.", gt=0),
    longPeriod: Optional[int] = Query(100, title="Long Period", description="", gt=0)
    ):
    """ Quickly runs the given indicator for the stock with only its default parameters."""
    fin = Stock(ticker=ticker, start=start, end=end, website=website, save=save, auto_load=False)
    # try block ?
    fin.load()
    results = fin.get_indicator('dual_moving_average', column=column, short_period=shortPeriod, long_period=longPeriod)
    #
    # {'Buy': sig_buy, 'Sell': sig_sell, 'Short': short_avg, 'Long': long_avg, 'Earnings': earnings} 
    #
    results['Short'].dropna(inplace=True)
    results['Long'].dropna(inplace=True)
    #
    short_period = results['Short'].to_dict()
    long_period = results['Long'].to_dict()
    #
    cleaned = {}
    cleaned['Short'] = { ts.isoformat(): val for ts, val  in short_period.items()}
    cleaned['Long'] = { ts.isoformat(): val for ts, val  in long_period.items()}
    cleaned['Buy'] = Utils.remove_nulls(results['Buy'], index=fin.dataframe.index)
    cleaned['Sell'] = Utils.remove_nulls(results['Sell'], index=fin.dataframe.index)
    cleaned['Earnings'] = [(ts.isoformat(), val) for ts, val in results['Earnings']]
    #
    return json.loads(json.dumps(cleaned, default=Utils.convert_numpy_types))

@router.get('/indicator/dema/{ticker}/')
async def get_dema(
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID."),
    start: Optional[str] = Query(Defaults.START_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="Start Date", description="The starting day in YYYY-MM-DD format."),
    end: Optional[str] = Query(Defaults.END_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="End Date", description="The ening day in YYYY-MM-DD format."),
    website: Optional[str] = Query("yahoo", title="Website", description="Which website to pull stock data from."),
    save: Optional[bool] = Query(True, title="Save", description="Update and save the results on local disk."),
    column: Optional[str] = Query("Close", title="Dataframe Column", description="Which dataframe column to perform the calculations on."),
    shortPeriod: Optional[int] = Query(20, title="Short Period", description="The Period for the MFI.", gt=0),
    longPeriod: Optional[int] = Query(50, title="Long Period", description="", gt=0)
    ):
    """ Quickly runs the given indicator for the stock with only its default parameters."""
    fin = Stock(ticker=ticker, start=start, end=end, website=website, save=save, auto_load=False)
    # try block ?
    fin.load()
    results = fin.get_indicator('dema', column=column, short_period=shortPeriod, long_period=longPeriod)
    #
    # {'Buy': sig_buy, 'Sell': sig_sell, 'Short': DEMA_short, 'Long': DEMA_long, 'Earnings': earnings} 
    #
    results['Short'].dropna(inplace=True)
    results['Long'].dropna(inplace=True)
    #
    short_period = results['Short'].to_dict()
    long_period = results['Long'].to_dict()
    #
    cleaned = {}
    cleaned['Short'] = { ts.isoformat(): val for ts, val  in short_period.items()}
    cleaned['Long'] = { ts.isoformat(): val for ts, val  in long_period.items()}
    cleaned['Buy'] = Utils.remove_nulls(results['Buy'], index=fin.dataframe.index)
    cleaned['Sell'] = Utils.remove_nulls(results['Sell'], index=fin.dataframe.index)
    cleaned['Earnings'] = [(ts.isoformat(), val) for ts, val in results['Earnings']]
    #
    return json.loads(json.dumps(cleaned, default=Utils.convert_numpy_types))

@router.get('/indicator/three_moving_average/{ticker}/')
async def get_three_moving_average(
    ticker: str = Path(..., title="Stock Ticker", description="A valid stock ticker ID."),
    start: Optional[str] = Query(Defaults.START_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="Start Date", description="The starting day in YYYY-MM-DD format."),
    end: Optional[str] = Query(Defaults.END_DATE, regex=r"\d{4}-\d{2}-\d{2}", title="End Date", description="The ening day in YYYY-MM-DD format."),
    website: Optional[str] = Query("yahoo", title="Website", description="Which website to pull stock data from."),
    save: Optional[bool] = Query(True, title="Save", description="Update and save the results on local disk."),
    column: Optional[str] = Query("Close", title="Dataframe Column", description="Which dataframe column to perform the calculations on."),
    shortPeriod: Optional[int] = Query(5, title="Short Period", description="The Period for the MFI.", gt=0),
    mediumPeriod: Optional[int] = Query(21, title="Medium Period", description=".", gt=0),
    longPeriod: Optional[int] = Query(63, title="Long Period", description="", gt=0)
    ):
    """ Quickly runs the given indicator for the stock with only its default parameters."""
    fin = Stock(ticker=ticker, start=start, end=end, website=website, save=save, auto_load=False)
    # try block ?
    fin.load()
    results = fin.get_indicator('three_moving_average', column=column, short_period=shortPeriod, medium_period=mediumPeriod, long_period=longPeriod)
    #
    # { 'Buy': sig_buy, 'Sell': sig_sell, 'Short': short_ema, 'Medium': medium_ema, 'Long': long_ema, 'Earnings': earnings}  
    #
    results['Short'].dropna(inplace=True)
    results['Medium'].dropna(inplace=True)
    results['Long'].dropna(inplace=True)
    #
    short_period = results['Short'].to_dict()
    medium_period = results['Medium'].to_dict()
    long_period = results['Long'].to_dict()
    #
    cleaned = {}
    cleaned['Short'] = { ts.isoformat(): val for ts, val  in short_period.items()}
    cleaned['Medium'] = { ts.isoformat(): val for ts, val  in medium_period.items()}
    cleaned['Long'] = { ts.isoformat(): val for ts, val  in long_period.items()}
    cleaned['Buy'] = Utils.remove_nulls(results['Buy'], index=fin.dataframe.index)
    cleaned['Sell'] = Utils.remove_nulls(results['Sell'], index=fin.dataframe.index)
    cleaned['Earnings'] = [(ts.isoformat(), val) for ts, val in results['Earnings']]
    #
    return json.loads(json.dumps(cleaned, default=Utils.convert_numpy_types))

