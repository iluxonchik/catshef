from catshef.snackbar import SnackBar

from allauth.account.signals import user_signed_up
from django.dispatch import receiver

USER_SIGNED_UP = ('{'
            'message: "Registration successful, please confirm your email address",'
            'actionHandler: function(event) { window.location.href = "/account/email/" },'
            'actionText: "Email Settings",'
            'timeout: 10000'
            '}')

@receiver(user_signed_up)
def set_snackbar(request, user, **kwargs):
    SnackBar.add_data(request, USER_SIGNED_UP)
