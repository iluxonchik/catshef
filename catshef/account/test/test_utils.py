from catshef.exceptions import ArgumentError

from account.utils import is_email_verified
from django.contrib.auth.models import User

from allauth.account.views import signup
from allauth.account.models import EmailAddress

from django.test import TestCase

class EmailVerificationTestCase(TestCase):    
    def test_email_not_verified(self):
        data = {'name':'jason', 'email':'jay@son.com', 
        'password1':'hellothere123', 'password2':'hellothere123'}
        self.client.post('/account/signup/', data=data)

        u = User.objects.get(email='jay@son.com')
        self.assertFalse(is_email_verified(u))

        # emulate email confirmed
        e = EmailAddress.objects.get(user=u)
        e.verified = True
        e.save()

        self.assertTrue(is_email_verified(u))
    
    def test_email_verified(self):
        data = {'name':'jason', 'email':'jay@son.com', 
        'password1':'hellothere123', 'password2':'hellothere123'}
        self.client.post('/account/signup/', data=data)

        u = User.objects.get(email='jay@son.com')

        # emulate email confirmed
        e = EmailAddress.objects.get(user=u)
        e.verified = True
        e.save()

        self.assertTrue(is_email_verified(u))

    def test_argument_error(self):
        with self.assertRaises(ArgumentError):
            is_email_verified()



