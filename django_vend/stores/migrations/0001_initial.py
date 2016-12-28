# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-28 09:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vend_auth', '0008_remove_venduser_users'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendOutlet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(editable=False)),
                ('name', models.CharField(max_length=256)),
                ('time_zone', models.CharField(max_length=256)),
                ('currency', models.CharField(max_length=256)),
                ('currency_symbol', models.CharField(max_length=32)),
                ('display_prices_tax_inclusive', models.BooleanField(default=True)),
                ('deleted_at', models.DateTimeField(null=True)),
                ('retailer', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='vend_auth.VendRetailer')),
            ],
        ),
        migrations.CreateModel(
            name='VendRegister',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(editable=False)),
                ('name', models.CharField(max_length=256)),
                ('invoice_prefix', models.CharField(max_length=32)),
                ('invoice_suffix', models.CharField(max_length=32)),
                ('invoice_sequence', models.PositiveIntegerField()),
                ('deleted_at', models.DateTimeField(null=True)),
                ('is_open', models.BooleanField(default=False)),
                ('register_open_time', models.DateTimeField(blank=True, null=True)),
                ('register_close_time', models.DateTimeField(blank=True, null=True)),
                ('outlet', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='vend_stores.VendOutlet')),
                ('retailer', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='vend_auth.VendRetailer')),
            ],
        ),
    ]