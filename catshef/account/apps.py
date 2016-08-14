from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'account'
    label = 'catshef_account'  # naming conflict with allauth.account
