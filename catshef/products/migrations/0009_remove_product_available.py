# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-08 20:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_auto_20160808_1335'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='available',
        ),
    ]