"""
Utility functions.
"""
from catshef.exceptions import ArgumentError
from allauth.account.models import EmailAddress

def is_email_verified(user=None, request=None):
    """
    Checks if the provided user has his email address verified.

    If user is provided, request argument is ignored.
    """
    # TODO: write tests
    if not user and not request:
        raise ArgumentError('user or request arguments must be provided')
    
    if not user:
        user = request.user

    return EmailAddress.objects.filter(user=user, verified=True).exists()

