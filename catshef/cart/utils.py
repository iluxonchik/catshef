import collections

from cart.exceptions import QueryParamsError
from catshef.exceptions import ArgumentError

from products.models import Product, ProductOption

from django.shortcuts import get_object_or_404
from decimal import Decimal

def _parse_int(value, name='value'):
    try:
       value = int(value)
    except ValueError:
        raise ArgumentError('{} must be an int '
                        '(or something that can be coerced to it)'.format(name))
    return value

def _parse_bool(value, name='value'):
    """
    Parses boolean value from its POST data representation.
    If parsing fails, it raises a value error.

    Accepted values for bool: 
    * 'True', 'true', '1' --> return True
    * 'False', 'false', '0' --> return False
    Anything else raises ArgumentError.

    Reasoning behind muliple values for each bool: easily usible from
    Python ('True'/'False'), JavaScript ('true', 'false') and by other
    languages in general ('0'/'1' and 0/1)
    """
    # NOTE: yes, not the best code, but in a hurry. It's pretty straighforward,
    # though.
    res = False  # just initializing
    if isinstance(value, str):
        if value in ('True', 'true', '1'):
            res = True
        elif value in ('False', 'false', '0'):
            res = False
    else:
        try:
            num = int(value)
            if num == 1:
                res = True
            elif num == 0:
                res = False
            else:
                raise ArgumentError('Invalid int value "{}"" for bool "{}"'.
                    format(value, name))
        except ValueError:
            raise ArgumentError('Value "{}" for bool "{}"" is invalid'.
                format(value, name))
    return res



def add_item_build_json_response(cart, product, options=[]):
    """
    Builds JSON response for items added to cart. If the item sepcified by
    product and options is not found in the cart, the resulting JSON response
    contains all values set to 0.
    """
    # init result
    res = {}

    item = cart._get_item(product=product, options=options)
    if item is not None:
        res['quantity'] = float(item['quantity'])
        res['total_options_price'] = float(item['total_options_price'])
        res['total_final_price'] = float(item['total_final_price'])
    else:
        res['quantity'] = 0
        res['total_options_price'] = 0
        res['total_final_price'] = 0

    return res

def parse_POST(request):
    """
    Parse post args and retrieve the related product and options (if applies).
    """
    res = { 'add_with_default_options' : False }
    product_pk = request.POST.get('product_pk')
    
    product_pk = _parse_int(product_pk, 'product_pk')

    if product_pk is None:
        raise QueryParamsError('product_pk not provided')

    res['product'] = get_object_or_404(Product, pk=product_pk)

    # a little hack, since you can't instruct getlist() to return None,
    # -1 here acts as a None 
    options_pks = request.POST.getlist('options_pks', -1)
    if options_pks == -1:
        options_pks = None
    else:
        if len(options_pks) == 1 and options_pks[0] == '':
            # if request.POST['option_pks'] contains '', it means that the product
            # is beign added without options EXPLICITLY
            options_pks = []

    if options_pks is not None:
        # if it's None, then the product will be added with defaults
        if not isinstance(options_pks, collections.Iterable):
            raise ArgumentError('option_pks must be an iterable')
        res['options'] = [get_object_or_404(ProductOption, pk=pk) 
                                                    for pk in options_pks]
    else:
        # options were not passed, not even an empty list, so add with defaults
        res['options'] = None  # avoids ifs in view
        res['add_with_default_options'] = True

    quantity = request.POST.get('quantity', 1)
    res['quantity'] = _parse_int(quantity)
    update_quantity = request.POST.get('update_quantity', False)
    res['update_quantity'] = _parse_bool(update_quantity, 'update_quantity')

    return res