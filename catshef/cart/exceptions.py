class NegativeQuantityException(ValueError):
    """
    The quantity argument passed in is neagative.
    """
    pass

class ProductUnavailableException(ValueError):
    """
    The product being added is unavailable.
    """
    pass

class ProductStockZeroException(ValueError):
    """
    The product being added has its stock set at zero.
    """
    pass

class QueryParamsError(ValueError):
    """
    There is a problem with the query parameters (applies to views in Cart).
    """
    pass