import account.views as views

from django.test import TestCase, SimpleTestCase
from django.core.urlresolvers import resolve


BASE_URL = '/account/'

class AccountURLsTestCase(TestCase):
    """
    Test account urls.
    """
    def test_root_url_uses_profile(self):
        root = resolve(BASE_URL)

        self.assertEqual(root.func, views.profile)
        self.assertEqual(root.func.__name__, 'profile')

    def test_profile_edit_url(self):
        pedit = resolve(BASE_URL + 'profile/')
        self.assertEqual(pedit.view_name,
            'edit_profile')
        self.assertEqual(pedit.func.__name__, 'edit_profile')

class AllauthURLsTestCase(TestCase):
    """
    Test that allauths urls are working as expected.
    """

    def test_login_url(self):
        res = resolve(BASE_URL + 'login/')
        self.assertEqual(res.url_name, 'account_login')

    def test_signup_url(self):
        res = resolve(BASE_URL + 'signup/')
        self.assertEqual(res.url_name, 'account_signup')

    def test_logout_url(self):
        res = resolve(BASE_URL + 'logout/')
        self.assertEqual(res.url_name, 'account_logout')

    def test_password_change_url(self):
        res = resolve(BASE_URL + 'password/change/')
        self.assertEqual(res.url_name, 'account_change_password')

    def test_password_set_url(self):
        res = resolve(BASE_URL + 'password/set/')
        self.assertEqual(res.url_name, 'account_set_password')

    def test_email_url(self):
        res = resolve(BASE_URL + 'email/')
        self.assertEqual(res.url_name, 'account_email')

    def test_confirm_email_url(self):
        res = resolve(BASE_URL + 'confirm-email/')
        self.assertEqual(res.url_name, 'account_email_verification_sent')

    def test_confirm_email_key_url(self):
        res = resolve(BASE_URL + 'confirm-email/something/')
        self.assertEqual(res.url_name, 'account_confirm_email')

    def test_password_reset_url(self):
        res = resolve(BASE_URL + 'password/reset/')
        self.assertEqual(res.url_name, 'account_reset_password')

    def test_password_reset_done(self):
        res = resolve(BASE_URL + 'password/reset/done/')
        self.assertEqual(res.url_name, 'account_reset_password_done')

    def test_password_reset_key_url(self):
        res = resolve(BASE_URL + 'password/reset/key/A-B/')
        self.assertEqual(res.url_name, 'account_reset_password_from_key')

    def test_password_reset_key_done_url(self):
        res = resolve(BASE_URL + 'password/reset/key/done/')
        self.assertEqual(res.url_name, 'account_reset_password_from_key_done')

