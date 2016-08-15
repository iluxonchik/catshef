from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
        related_name='profile')
    name = models.CharField(max_length=255, blank=True)
    phone = PhoneNumberField(blank=True)

    def __str__(self):
        return 'Profile for User with pk={} and email={}'.format(
            self.user.pk, self.user.email)
