""" Data validation and coercion """
import re
from datetime import datetime
from dateutil.parser import parse as parse_date
from eth_utils.address import is_address, to_normalized_address


class InvalidInput(ValueError):
    """ Exception thrown if an input var is the wrong type """
    pass


def be_integer(v):
    """ Try and make v an integer or throw """
    if isinstance(v, int):
        return v
    else:
        try:
            return int(v)
        except ValueError:
            raise InvalidInput("Input needs to be an integer")

def be_string(v):
    """ Try and make v a string """
    if isinstance(v, bytes):
        v = v.decode('utf-8')

    if not isinstance(v, str):
        raise InvalidInput("Input is not a string")

    return v

def be_hash(v):
    """ Make sure v is a hexidecimal hash """
    
    v = be_string(v)

    if not re.match(r'^(0x)?[A-Fa-f0-9]+$', v):
        raise InvalidInput("String is not a hash")

    if len(v) not in (64,66):
        raise InvalidInput("Hash is an invalid length")

    # Add the prefix if it doesn't have it
    if v[:2] != '0x':
        return '0x' + v
    else:
        return v

def be_address(v):
    """ Make sure v is an Ethereum address """
    
    v = be_string(v)

    if not is_address(v):
        raise InvalidInput("Address is invalid")

    # Add the prefix if it doesn't have it
    return to_normalized_address(v)

def be_datetime(v):
    """ Make sure v is a date """
    if isinstance(v, datetime):
        return v
    elif isinstance(v, str):
        try:
            return parse_date(v)
        except ValueError as e:
            raise InvalidInput(str(e))
    else:
        raise InvalidInput("Unable to parse %s as a date" % type(v))