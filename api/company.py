from .connections import Mongo
from .decorators import validate_classmethod
from .static import IEX_SECTORS, IEX_ISSUE_TYPES
from .iex import IEX
from . import CONFIG
"""
symbol  string  Ticker of the company
companyName     string  Name of the company
employees   number  Number of employees
exchange    string  Refers to Exchange using IEX Supported Exchanges list
industry    string  Refers to the industry the company belongs to
website     string  Website of the company
description     string  Description for the company
CEO     string  Name of the CEO of the company
securityName    string  Name of the security
issueType   string  Refers to the common issue type of the stock.
    ad - ADR
    cs - Common Stock
    cef - Closed End Fund
    et - ETF
    oef - Open Ended Fund
    ps - Preferred Stock
    rt - Right
    struct - Structured Product
    ut - Unit
    wi - When Issued
    wt - Warrant
    empty - Other
sector  string  Refers to the sector the company belongs to.
primarySicCode  string  Primary SIC Code for the symbol (if available)
tags    array   An array of strings used to classify the company.
address     string  Street address of the company if available
address2    string  Street address of the company if available
state   string  State of the company if available
city    string  City of the company if available
zip     string  Zip code of the company if available
country     string  Country of the company if available
phone   string  Phone number of the company if available
"""


class Company:
    _DB_NAME = CONFIG.DB_NAME
    _COLLECTION = 'companies'
    _SCHEMA = {
        "symbol": {'type': 'string', 'required': True, 'empty': False},
        "companyName": {'type': 'string', 'required': True, 'empty': False},
        "sector": {'type': 'string', 'required': True, 'empty': False},
        "employees": {'type': 'integer', 'nullable': True, 'coerce': int},
        "industry": {'type': 'string', 'default': "None"},
        "securityName": {'type': 'string'},
        "exchange": {'type': 'string'},
        "website": {'type': 'string', 'default': ""},
        "description": {'type': 'string', 'default': ""},
        "CEO": {'type': 'string', 'default': ""},
        "issueType": {'type': 'string', 'default': "empty"},
        "primarySicCode": {'type': 'integer', 'coerce': int, 'default': 0},
        "tags": {'type': 'list', 'schema': {'type': 'string'}, 'default': []},
        "address": {'type': 'string', 'default': ""},
        "address2": {'type': 'string', 'default': ""},
        "state": {'type': 'string', 'default': ""},
        "city": {'type': 'string', 'default': ""},
        "zip": {'type': 'string', 'default': ""},
        "country": {'type': 'string', 'default': ""},
        "phone": {'type': 'string', 'default': ""},
    }

    @classmethod
    @validate_classmethod
    def fetch_iex_data(cls, symbol):
        iex = IEX(ticker=symbol)
        try:
            data = iex.company()
            if data['sector'] == '':
                data['sector'] = "Miscellaneous"
            return False, data
        except Exception as e:
            # TODO: handle HTTP errors
            return True, e

    @classmethod
    def get_by_symbol(cls, symbol):
        with Mongo() as client:
            collection = client[cls._DB_NAME][cls._COLLECTION]
            data = collection.find_one({'symbol': symbol.upper()}, {'_id': 0})
            if data:
                return data
            # Get from iex
            error, data = cls.fetch_iex_data(symbol)
            if error:
                return {'Error': data}
            # Add company
            collection.insert_one(data)
            # No fucking clue why but the _id magically appears in the object
            data.pop('_id', None)
            return data

    @classmethod
    def get_symbols(cls, skip, limit, issueType=None, sector=None):
        query = {}
        if issueType and issueType.lower() in IEX_ISSUE_TYPES:
            query['issueType'] = issueType
        if sector and sector in IEX_SECTORS:
            query['sector'] = sector
        with Mongo() as client:
            collection = client[cls._DB_NAME][cls._COLLECTION]
            total = collection.count(query)
            results = [x['symbol'] for x in collection.find(
                query, {'symbol': 1, '_id': 0}, skip=skip, limit=limit)]
            return {'total': total, 'symbols': results}
