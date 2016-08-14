from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
        related_name='profile')
    name = models.CharField(max_length=255)
    phone = PhoneNumberField(blank=True)
