from datetime import datetime
from uuid import UUID

from django.utils.timezone import make_aware, now, FixedOffset
from django.test import TestCase

from django_vend.auth.models import VendRetailer
from .models import VendOutlet
from .forms import VendOutletForm


class VendOutletFormTestCase(TestCase):

    def setUp(self):
        self.retailer = VendRetailer(
            name="TestRetailer",
            access_token="some token",
            expires=now(),
            expires_in=0,
            refresh_token="some other token",
        )
        self.retailer.save()

    def test_form(self):
        uid = "dc85058a-a683-11e4-ef46-e8b98f1a7ae4"
        name = "Main Outlet"
        tz = "Pacific/Auckland"
        currency = "NZD"
        symbol = "$"
        data = {
            "id": uid,
            "name": name,
            "time_zone": tz,
            "default_tax_id": "b1d192bc-f019-11e3-a0f5-b8ca3a64f8f4",
            "currency": currency,
            "currency_symbol": symbol,
            "display_prices": "inclusive",
            "deleted_at": "2014-07-01T20:22:58+00:00",
            "version": 1288421
        }

        form = VendOutletForm(data)
        form.instance.retailer = self.retailer
        form.instance.retrieved = now()

        self.assertTrue(form.is_valid())

        if form.is_valid():
            instance = form.save()

        del_time = make_aware(datetime(2014, 7, 1, 20, 22, 58), FixedOffset(0))

        self.assertEqual(instance.uid, UUID(uid))
        self.assertEqual(instance.name, name)
        self.assertEqual(instance.time_zone, tz)
        self.assertEqual(instance.currency, currency)
        self.assertEqual(instance.display_prices_tax_inclusive, True)
        self.assertTrue(instance.deleted_at == del_time)

    def test_override_instance(self):
        uid = "dc85058a-a683-11e4-ef46-e8b98f1a7ae4"
        name = "Main Outlet"
        tz = "Pacific/Auckland"
        currency = "NZD"
        symbol = "$"
        data = {
            "id": uid,
            "name": "London Outlet",
            "time_zone": tz,
            "default_tax_id": "b1d192bc-f019-11e3-a0f5-b8ca3a64f8f4",
            "currency": currency,
            "currency_symbol": symbol,
            "display_prices": "inclusive",
            "deleted_at": "2014-07-01T20:22:58+00:00",
            "version": 1288421
        }
        VendOutlet.objects.create(uid=uid, name=name, time_zone=tz,
            currency=currency, currency_symbol=symbol, retailer=self.retailer,
            retrieved=now())
        outlets = VendOutlet.objects.all()

        self.assertEqual(len(outlets), 1)
        instance = outlets[0]
        self.assertEqual(instance.name, name)


        form = VendOutletForm(data)
        form.instance.retailer = self.retailer
        form.instance.retrieved = now()

        self.assertTrue(form.is_valid())

        if form.is_valid():
            instance = form.save()

        del_time = make_aware(datetime(2014, 7, 1, 20, 22, 58), FixedOffset(0))

        self.assertEqual(instance.uid, UUID(uid))
        self.assertEqual(instance.name, "London Outlet")
        self.assertEqual(instance.time_zone, tz)
        self.assertEqual(instance.currency, currency)
        self.assertEqual(instance.display_prices_tax_inclusive, True)
        self.assertTrue(instance.deleted_at == del_time)

        outlets = VendOutlet.objects.all()

        self.assertEqual(len(outlets), 1)
        self.assertEqual(instance.name, "London Outlet")
