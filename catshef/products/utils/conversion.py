"""
products utility functions
"""
from decimal import Decimal, ROUND_HALF_UP
from catshef.exceptions import ArgumentError

import collections

def round_decimal(value, precision=2, rounding=ROUND_HALF_UP):
    """
    Round a Decimal to the given precision.
    """
    if not isinstance(value, Decimal):
        raise ArgumentError('value must be a decimal.Decimal')

    return (value.quantize(Decimal(10) ** -precision, rounding=rounding) 
        if value is not None 
        else value)

def to_decimal(val, rounding=round_decimal):
    """
    Convers a value or list of values to Decimal.

    Arguments:
        * val - value(s) to convert
        * rounding - callable wich takes a Decimal as an argument and returns
          a Decimal. Applied to every value in val.
    """
    if isinstance(val, str):
        val = (val, )

    if not isinstance(val, collections.Iterable):
        val = (val, )

    ret_generator = True
    if len(val) == 1:
        ret_generator = False

    if rounding:
        res = (rounding(Decimal(value)) for value in val)
    else:
        res= (Decimal(value) for value in val)
    
    if not ret_generator:
        res = next(res)
    
    return res

