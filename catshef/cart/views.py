"""
All of the cart manipulation views work only on AJAX request and are
REST-ish.

On success, they return some information about the manipulated object.
In both, success and failure, a message can be passed (this one should probably
be displayed as a snackbar to the user).
"""
import json

from cart.cart import Cart
from cart.utils import (parse_add_to_cart_POST, parse_remove_from_cart_POST,
    add_to_cart_from_post_data, remove_from_cart_from_post_data)

from catshef.exceptions import ArgumentError

from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse


def add_to_cart(request):
    """
    Responsible for adding/updating items in cart.
    All data must be provided via POST(for security reasons).

    Request POST data description:
        * product_pk (str or int): PK of product to be added.
        * options_pks (empty str or list of strs or list of ints): product 
            options. If you want  to add a product without options explicitly, 
            set this to an EMPTY STRING (''). If you want to provide options, 
            set this to a list of ints, where ints are PKs of options to be 
            added. If this parameter is omitted, prodcut will be added to cart 
            with its DEFAULT OPTIONS.
        * quantity (str or int): quantity of the product to be added to the cart. If
            omitted, defaults to 1.
        * update_quantity (str or int): whether cart quantity should be updated
            or incremented by `quantity`. 

            Valid values: 'True', 'true', '1', 1
            (evaluate to True) and 'False', 'false', '0', 0 (evalueate to 
            False). Anything else will raise ArgumentError.

    Returns:
        Added data description, if data was added (even if 0 quantity was added)
        JSON with a "message" key, which describes the error.

    NOTE: any returned data can contain a "message" key
    """
    if request.method == 'POST':
        cart = Cart(request)
        try:
            post = parse_add_to_cart_POST(request)  # can raise Http404 or ArgumentError
        except ArgumentError as err:
            raise Http404(str(err))

        status_code, res_dict = add_to_cart_from_post_data(cart, post)
        return JsonResponse(res_dict, status=status_code)

    else:
        raise Http404()  # 404 instead of 403 is here on purpose (https://tools.ietf.org/html/rfc7231.html#page-59)

def remove_from_cart(request):
    """
    Responsible for remobing items form cart.

    All data must be provided via POST(for security reasons).

    Request POST data description:
        * product_pk (str or int): PK of product to be removed.
        * options_pks (empty str or list of strs or list of ints): product 
            options. If you want  to remove a product without options explicitly, 
            set this to an EMPTY STRING (''). If you want to provide options, 
            set this to a list of ints, where ints are PKs of options. 
            If this parameter is omitted, prodcut will be added to cart 
            with its DEFAULT OPTIONS.

    Returns:
        Removed data description, if data was removed.
        JSON with a "message" key, which describes the error.

    NOTE: any returned data can contain a "message" key.
    """ 
    if request.method == 'POST':
        cart = Cart(request)
        try:
            post = parse_remove_from_cart_POST(request)  # can raise Http404 or ArgumentError
        except ArgumentError as err:
            raise Http404(str(err))

        status_code, res_dict = remove_from_cart_from_post_data(cart, post)
        return JsonResponse(res_dict, status=status_code)

    else:
        raise Http404()  # 404 instead of 403 is here on purpose (https://tools.ietf.org/html/rfc7231.html#page-59)

def clear_cart(request):
    """
    Responsible for clearing the cart.

    This view expects no data, just a POST request is enough.

    Request must be via POST (for security reasons)
    """
    if request.method == 'POST':
        cart = Cart(request)
        status_code = 204 if cart.has_items() else 304
        cart.clear()
        return HttpResponse(status=status_code)
    else:
        raise Http404()  # 404 instead of 403 is here on purpose (https://tools.ietf.org/html/rfc7231.html#page-59) 
