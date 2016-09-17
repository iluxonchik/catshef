import collections
from decimal import Decimal

from cart.exceptions import (QueryParamsError, NegativeQuantityException,
ProductUnavailableException, ProductStockZeroException)

from catshef.exceptions import ArgumentError

from products.models import Product, ProductOption

from django.http import Http404
from django.shortcuts import get_object_or_404

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


def get_cart_item_json_response(cart, product, options=[]):
    """
    Builds JSON response for items added to cart. If the item sepcified by
    product and options is not found in the cart, the resulting JSON response
    contains all values set to 0.
    """
    # init result
    res = {}

    item = cart._get_item(product=product, options=options)
    
    res['product_pk'] = product.pk
    res['options_pks'] = ([option.pk for option in options] 
                                                if len(options) > 0  else '')
    if item is not None:
        # item in cart
        res['quantity'] = float(item['quantity'])
        res['total_options_price'] = float(item['total_options_price'])
        res['total_final_price'] = float(item['total_final_price'])
    else:
        # item not in cart
        res['quantity'] = 0
        res['total_options_price'] = 0
        res['total_final_price'] = 0

    return res

def parse_POST(request):
    """
    Parse post args and retrieve the related product and options (if applies).
    """
    res = {}

    product_pk = request.POST.get('product_pk')
    product_pk = _parse_int(product_pk, 'product_pk')

    if product_pk is None:
        raise QueryParamsError('product_pk not provided')

    product = get_object_or_404(Product, pk=product_pk)
    res['product'] = product

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
        res['options'] = product.get_default_options()

    quantity = request.POST.get('quantity', 1)
    res['quantity'] = _parse_int(quantity)
    update_quantity = request.POST.get('update_quantity', False)
    res['update_quantity'] = _parse_bool(update_quantity, 'update_quantity')

    return res

def get_status_code(quantity, update_quantity):
    """
    Returns 201 if the cart was changed by addition, 304 otherwise.
    """
    return 304 if quantity == 0 and not update_quantity else 201

def add_to_cart_from_post_data(cart, post_data):    
    """
    Wrapper arroung cart.cart.Cart.add() and 
    cart.cart.Cart.add_with_default_options() that calls the approptiate
    function and returns the approptiate response dict, as well as status code.

    This function is here to prevent putitng a lot of logic in the views.

    Returns a tuple consisting of status code and response dictionary (in that
    order).
    """
    message = None
    try:
        cart.add(product=post_data['product'], options=post_data['options'],
            quantity=post_data['quantity'], 
            update_quantity=post_data['update_quantity'])
        status_code = get_status_code(post_data['quantity'], 
                                                post_data['update_quantity'])
    except (NegativeQuantityException,
        ProductUnavailableException, ProductStockZeroException) as ex:
        status_code = 400
        message = str(ex)
    except Http404 as ex:
        status_code = 404
        message = str(ex)
    except Exception as ex:
        # some other error
        status_code = 400
        message = 'Error: ' + str(ex)

    if status_code < 400:
        res_dict = get_cart_item_json_response(cart=cart, 
            product=post_data['product'], options=post_data['options'])
    else:
        res_dict = {'message': message}

    return (status_code, res_dict)