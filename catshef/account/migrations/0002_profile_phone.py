# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-14 20:42
from __future__ import unicode_literals

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('catshef_account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128),
        ),
    ]
