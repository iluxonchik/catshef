from django.test import TestCase
from account.models import Profile
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User


class ProfileModelTestCase(TestCase):

    def test_profile_basic(self):
        u = User.objects.create(username='jason', email='jay@son.com',
            password='jaysonrules')
        profile = Profile.objects.create(user=u, phone='+351960000000',
            name='Jason')
        prof = Profile.objects.get(user=u)

        self.assertEqual(prof.user, u)
        self.assertEqual(str(prof.phone), '+351960000000')
        self.assertEqual(prof.name, 'Jason')

        self.assertEqual(u.profile, profile)

        # Profile without a phone number test
        u = User.objects.create(username='harry', email='har@ry.com',
            password='harryrules')
        profile = Profile.objects.create(user=u, name='John')
        prof = Profile.objects.get(user=u)

        prof = Profile.objects.get(user=u)

        self.assertEqual(prof.user, u)
        self.assertEqual(str(prof.phone), '')
        self.assertEqual(prof.name, 'John')

        self.assertEqual(u.profile, profile)