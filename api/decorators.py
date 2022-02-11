from cerberus import Validator
from functools import wraps


def validate_classmethod(f):
    @wraps(f)
    def _wrapper(cls, *args, **kwargs):
        error, response = f(cls, *args, **kwargs)
        if error:
            return error, response
        v = Validator(cls._SCHEMA, purge_unknown=True)
        norm_resp = v.normalized(response)

        is_valid = v.validate(norm_resp)
        if not is_valid:
            return True, v.errors
        return False, v.document
    return _wrapper


def requires_dataframe(f):
    @wraps(f)
    def _wrapper(cls, *args, **kwargs):
        if not hasattr(cls, '_dataframe'):
            # TODO: Custom exception or return error object?
            raise Exception('DataFrame not loaded yet.')
        return f(cls, *args, **kwargs)
    return _wrapper


def validate_kwargs(schema):
    def _decorator(f):
        @wraps(f)
        def _wrapper(*args, **kwargs):
            v = Validator(schema, purge_unknown=True)
            norm_kwargs = v.normalized(kwargs)
            is_valid = v.validate(norm_kwargs)
            if not is_valid:
                raise Exception(f"Error validating kwargs: {v._errors}.")
            return f(*args, **v.document)
        return _wrapper
    return _decorator

# def contract_resolver(f):
#     @wraps(f)
#     def _wrapper(cls, *args, **kwargs):
#         return f(cls, contract, *args, **kwargs)
#     return _wrapper
