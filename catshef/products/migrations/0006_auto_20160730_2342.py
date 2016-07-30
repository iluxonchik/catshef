# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-30 23:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_auto_20160730_2340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='nutrition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.ProductNutrition'),
        ),
    ]