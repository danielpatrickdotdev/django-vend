# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-25 21:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vend_auth', '0007_auto_20161225_2051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='venduser',
            name='users',
        ),
    ]