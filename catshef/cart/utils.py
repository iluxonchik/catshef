from decimal import Decimal

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