"""
Custom context processors for 'accounts' app.
"""
from catshef.snackbar import SnackBar

def snackbar_data(request):
    """
    Gets any SnackBar code (if present) and passes it into context.

    For more info about snackbars go to: https://getmdl.io/components/index.html?#snackbar-section
    """
    snackbars = SnackBar.get(request)
    js = snackbars.get_js()

    return {'snackbar_js':js}
