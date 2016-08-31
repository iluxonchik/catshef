"""
products utility functions
"""
from decimal import Decimal, ROUND_HALF_UP
from catshef.exceptions import ArgumentError

def round_decimal(value, precision=2, rounding=ROUND_HALF_UP):
    """
    Round a Decimal to the given precision.
    """
    if not isinstance(value, Decimal):
        raise ArgumentError('value must be a decimal.Decimal')

    return (value.quantize(Decimal(10) ** -precision, rounding=rounding) 
        if value is not None 
        else value)