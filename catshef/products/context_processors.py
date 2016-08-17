"""
Custom context processors for 'products' app.
"""
from allauth.account.forms import SignupForm

def site_name(request):
    """
    Sets the site name in context. Since the name of the site is not yet
    decided, this will allow to change it dynamically.
    """
    return {'site_name':'CatFood'}

def login_modal_form(self):
    """
    Puts the login modal form in the context.
    """
    return {'modal_signup_form':SignupForm()}