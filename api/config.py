import os
from cerberus import Validator
#
_schema = {
    'DATA_LOCATION': {'type': 'string'},
    'IEX_API_KEY': {'type': 'string'},
    'IEX_TOKEN': {'type': 'string'},
    'COINMARKETCAP_API_KEY': {'type': 'string'},
    'DB_NAME': {'type': 'string'},
    'OPTIONS_FEES': {'type': 'float', 'coerce': float},
    'ALPHA_VANTAGE_KEY': {'type': 'string'}
}
#
_env_validator = Validator(_schema, purge_unknown=True)
#
_env_dict = {
    'DATA_LOCATION': os.getenv('DATA_LOCATION'),
    'IEX_API_KEY': os.getenv('IEX_API_KEY'),
    'IEX_TOKEN': os.getenv('IEX_TOKEN'),
    'COINMARKETCAP_API_KEY': os.getenv('COINMARKETCAP_API_KEY'),
    'DB_NAME': os.getenv('DB_NAME'),
    'OPTIONS_FEES': os.getenv('OPTIONS_FEES', '0.0'),
    'ALPHA_VANTAGE_KEY': os.getenv('ALPHA_VANTAGE_KEY')
}
#
norm_data = _env_validator.normalized(_env_dict)
if not _env_validator.validate(norm_data):
    raise Exception(f"ENV Validation Errors: {_env_validator.errors}.")
#
_env = _env_validator.document
#


class CONFIG:
    DATA_LOCATION = _env.get('DATA_LOCATION')
    IEX_API_KEY = _env.get('IEX_API_KEY')
    IEX_TOKEN = _env.get('IEX_TOKEN')
    COINMARKETCAP_API_KEY = _env.get('COINMARKETCAP_API_KEY')
    DB_NAME = _env.get('DB_NAME')
    OPTIONS_FEES = _env.get('OPTIONS_FEES')
    ALPHA_VANTAGE_KEY = _env.get('ALPHA_VANTAGE_KEY')
