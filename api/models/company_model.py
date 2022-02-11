from .static import IEX_SECTORS, IEX_ISSUE_TYPES

class CompanyModel:
    _SCHEMA = {
        "symbol": {'type': 'string', 'required': True, 'empty': False},
        "companyName": {'type': 'string', 'required': True, 'empty': False},
        "sector":{'type': 'string', 'required': True, 'empty': False},
        "employees": {'type': 'integer', 'nullable': True, 'coerce': int},
        "industry": {'type': 'string', 'default': "None"},
        "securityName":{'type': 'string'},
        "exchange":{'type': 'string'},
        "website": {'type': 'string', 'default': ""},
        "description":{'type': 'string', 'default': ""},
        "CEO":{'type': 'string', 'default': ""},
        "issueType":{'type': 'string', 'default': "empty"},
        "primarySicCode": {'type': 'integer', 'coerce': int, 'default': 0 },
        "tags": {'type': 'list', 'schema': {'type': 'string'}, 'default': []},
        "address": {'type': 'string', 'default': ""},
        "address2":{'type': 'string', 'default': ""},
        "state":{'type': 'string', 'default': ""},
        "city":{'type': 'string', 'default': ""},
        "zip":{'type': 'string', 'default': ""},
        "country":{'type': 'string', 'default': ""},
        "phone":{'type': 'string', 'default': ""},
    }
    
    @property
    def symbol(self):
        """
        string  Ticker of the company
        """
        return self._symbol
    
    @property
    def companyName(self):
        """
        string  Name of the company
        """
        return self._companyName
    
    @property
    def sector(self):
        """
        string  Refers to the sector the company belongs to.
        """
        return self._sector
    
    @property
    def employees(self):
        """
        number  Number of employees
        """
        return self._employees
    
    @property
    def industry(self):
        """
        string  Refers to the industry the company belongs to
        """
        return self._industry
    
    @property
    def securityName(self):
        """
        string  Name of the security
        """
        return self._securityName
    
    @property
    def exchange(self):
        """
        string  Refers to Exchange using IEX Supported Exchanges list
        """
        return self._exchange
    
    @property
    def website(self):
        """
        string  Website of the company
        """
        return self._website
    
    @property
    def description(self):
        """
        string  Description for the company
        """
        return self._description
    
    @property
    def CEO(self):
        """
        string  Name of the CEO of the company
        """
        return self._CEO
    
    @property
    def issueType(self):
        """
        string  Refers to the common issue type of the stock:
            * ad - ADR
            * cs - Common Stock
            * cef - Closed End Fund
            * et - ETF
            * oef - Open Ended Fund
            * ps - Preferred Stock
            * rt - Right
            * struct - Structured Product
            * ut - Unit
            * wi - When Issued
            * wt - Warrant
            * empty - Other
        """
        return self._issueType
    
    @property
    def primarySicCode(self):
        """
        string  Primary SIC Code for the symbol (if available)
        """
        return self._primarySicCode
    
    @property
    def tags(self):
        """
        array   An array of strings used to classify the company.
        """
        return self._tags
    
    @property
    def address(self):
        """
        string  Street address of the company if available
        """
        return self._address
    
    @property
    def adderss2(self):
        """
        string  Street address of the company if available
        """
        return self._adderss2
    
    @property
    def state(self):
        """
        string  State of the company if available
        """
        return self._state
    
    @property
    def city(self):
        """
        string  City of the company if available
        """
        return self._city
    
    @property
    def zip(self):
        """
        string  Zip code of the company if available
        """
        return self._zip
    
    @property
    def country(self):
        """
        string  Country of the company if available
        """
        return self._country
    
    @property
    def phone(self):
        """
        string  Phone number of the company if available
        """
        return self._phone