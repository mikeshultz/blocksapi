""" Data validation and coercion """


class InvalidInput(ValueError):
    """ Exception thrown if an input var is the wrong type """
    pass


def beInteger(v):
    """ Try and make v an integer or throw """
    if type(v) == int:
        return v
    else:
        try:
            return int(v)
        except ValueError:
            raise InvalidInput("Input needs to be an integer")

def beString(v):
    """ Try and make v a string """
    if type(v) == bytes:
        v = v.decode('utf-8')

    if type(v) != str:
        raise InvalidInput("Input is not a string")

    return v

def beHash(v):
    """ Make sure v is a hexidecimal hash """
    
    v = beString(v)

    if not re.match(r'^(0x)?[A-Fa-f0-9]+$', v):
        raise InvalidInput("String is not a hash")

    # Add the prefix if it doesn't have it
    if v[:2] != '0x':
        return '0x' + v
    else:
        return v