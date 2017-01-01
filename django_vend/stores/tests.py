from datetime import datetime
from uuid import UUID

from django.utils.timezone import make_aware, now, FixedOffset
from django.test import TestCase

from django_vend.auth.models import VendRetailer
from .models import VendOutlet, VendRegister
from .forms import VendOutletForm, VendRegisterForm


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


class VendRegisterFormTestCase(TestCase):

    def setUp(self):
        self.retailer = VendRetailer.objects.create(
            name="TestRetailer",
            access_token="some token",
            expires=now(),
            expires_in=0,
            refresh_token="some other token",
        )

        self.outlet = VendOutlet.objects.create(
            uid="b8ca3a65-0183-11e4-fbb5-2816d2677218",
            name="Main Outlet",
            time_zone="Pacific/Auckland",
            currency="NZD",
            currency_symbol="$",
            retailer=self.retailer,
            retrieved=now()
        )

        self.uid = "dc85058a-a683-11e4-ef46-e8b98f1a7ae4"
        self.name = "Main Register"
        self.outlet_id = "b8ca3a65-0183-11e4-fbb5-2816d2677218"
        self.outlet = VendOutlet.objects.get(uid=self.outlet_id)
        self.data = {
            "id": self.uid,
            "name": self.name,
            "outlet_id": self.outlet_id,
            "ask_for_note_on_save": 1,
            "print_note_on_receipt": False,
            "ask_for_user_on_sale": False,
            "show_discounts_on_receipts": True,
            "print_receipt": True,
            "email_receipt": False,
            "invoice_prefix": "PRE",
            "invoice_suffix": "SUF",
            "invoice_sequence": 1234,
            "button_layout_id": "b8ca3a65-0183-11e4-fbb5-2816e25ffc51",
            "is_open": True,
            "register_open_time": "2015-03-16T22:21:50+00:00",
            "register_close_time": "null",
            "deleted_at": "2014-07-01T20:22:58+00:00",
            "version": 1288421
        }

        self.del_time = make_aware(datetime(2014, 7, 1, 20, 22, 58), FixedOffset(0))
        self.other_time = make_aware(datetime(2015, 3, 16, 22, 21, 50), FixedOffset(0))

    def test_form(self):
        form = VendRegisterForm(self.data)
        form.instance.retailer = self.retailer
        form.instance.retrieved = now()

        self.assertTrue(form.is_valid())

        if form.is_valid():
            instance = form.save()

        self.assertEqual(instance.uid, UUID(self.uid))
        self.assertEqual(instance.name, self.name)
        self.assertEqual(instance.outlet, self.outlet)
        self.assertEqual(instance.invoice_prefix, "PRE")
        self.assertEqual(instance.invoice_suffix, "SUF")
        self.assertEqual(instance.invoice_sequence, 1234)
        self.assertTrue(instance.deleted_at == self.del_time)
        self.assertTrue(instance.is_open)
        self.assertTrue(instance.register_open_time == self.other_time)
        self.assertIsNone(instance.register_close_time)
        self.assertEqual(instance.retailer, self.retailer)

    def test_override_instance(self):
        VendRegister.objects.create(
            uid=self.uid,
            name=self.name,
            outlet=self.outlet,
            invoice_prefix="PRE",
            invoice_suffix="SUF",
            invoice_sequence=1234,
            is_open=False,
            register_close_time=self.other_time,
            deleted_at=self.del_time,
            retailer=self.retailer,
            retrieved=now()
        )
        registers = VendRegister.objects.all()

        self.assertEqual(len(registers), 1)
        instance = registers[0]
        self.assertEqual(instance.name, self.name)
        self.assertEqual(instance.outlet, self.outlet)
        self.assertFalse(instance.is_open)
        self.assertIsNone(instance.register_open_time)
        self.assertEqual(instance.register_close_time, self.other_time)

        form = VendRegisterForm(self.data)
        form.instance.retailer = self.retailer
        form.instance.retrieved = now()

        self.assertTrue(form.is_valid())

        if form.is_valid():
            instance = form.save()

        self.assertEqual(instance.uid, UUID(self.uid))
        self.assertTrue(instance.deleted_at == self.del_time)
        self.assertTrue(instance.is_open)

        registers = VendRegister.objects.all()

        self.assertEqual(len(registers), 1)
        register = registers[0]
        self.assertTrue(register.register_open_time == self.other_time)
        self.assertIsNone(register.register_close_time)
