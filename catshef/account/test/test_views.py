from account import views

from django.contrib.auth.models import User, AnonymousUser

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.conf import settings

BASE_URL = '/account/'

class AccountBaseTestCase(TestCase):
    """
    Base test case that sets up the data shared by all test cases.
    """
    USERNAME = 'thegame'
    PASSWORD = 'The Protege Of The D.R.E.'

    def _setup_request(self, path):
        request = self.factory.get(path)
        request.sesion = {}
        request.user = AnonymousUser()
        return request

    def _login_user(self):
        self.client.login(username=AccountBaseTestCase.USERNAME,
            password=AccountBaseTestCase.PASSWORD)

    def setUp(self):
        self.factory = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        super(AccountBaseTestCase, cls).setUpTestData()
        User.objects.create_user(username=AccountBaseTestCase.USERNAME,
            email='thegame@dr.dre', password=AccountBaseTestCase.PASSWORD)


class ProfileViewTestCase(AccountBaseTestCase):

    def test_profile_redirects_to_login(self):
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, 302)
        self.assertIn(settings.LOGIN_URL, response['Location'])


    def test_profile_user_logged_in(self):
        self._login_user()
        request = self._setup_request(BASE_URL)
        
        with self.assertTemplateUsed('account/profile.html'):
            response = views.profile(request)

        self.assertEqual(response.status_code, 200)


class ProfileEditViewTestCase(AccountBaseTestCase):

    def test_edit_profile_redirects_to_login(self):   
        response = self.client.get(BASE_URL + 'profile/')
        self.assertEqual(response.status_code, 302)
        self.assertIn(settings.LOGIN_URL, response['Location'])


    def test_profile_edit_logged_in(self):
        self._login_user()
        request = self._setup_request(BASE_URL + 'profile/')
        
        with self.assertTemplateUsed('account/edit_profile.html'):
            response = views.profile(request)

        self.assertEqual(response.status_code, 200)
    






