"""
Custom context processors for 'products' app.
"""

def site_name(request):
    """
    Sets the site name in context. Since the name of the site is not yet
    decided, this will allow to change it dynamically.
    """
    return {'site_name':'CatFood'}