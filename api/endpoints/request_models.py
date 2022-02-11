from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field

class Defaults:
    START_DATE = str(datetime.today().date() - timedelta(days=365))
    END_DATE = str(datetime.today().date()) 
#############################
# General Models
#############################

class StockTicker(BaseModel):
    ticker: str = Field(..., title="Stock Ticker", description="A valid stock ticker ID.")

class TickersList(BaseModel):
    tickers: List[str] = Field(..., title="Stock Tickers", description="A valid stock ticker IDs.")

#############################
# Sentiment Models
#############################

class ZeroShotParams(BaseModel):
    """limit=0, lang='en', key_names=['headline', 'summary'], canidate_labels=['positive', 'negative', 'neutral']"""
    limit: int = Field(
            25,
            title="Batch Limit",
            description="Limit the number of records to be processed.",
            gt=0,
            lte=25)
    lang: str = Field(
            'en',
            title="Language",
            description="The languange code to use with zero shot.")
    key_names: List[str] = Field(
            ['headline', 'summary'],
            title="Key Names",
            description="Key names from the news object to apply the funtion to.")
    canidate_labels: List[str] = Field(
            ['positive', 'negative', 'neutral'],
            title="Canidate Labels",
            description="Labels to attempt to classify from the text.")
