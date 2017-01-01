from django import forms
from django.utils.dateparse import parse_datetime
from django.test import TestCase

from .forms import VendDateTimeField


class VendDateTimeForm(forms.Form):
    date = VendDateTimeField()

class VendOptionalDateTimeForm(forms.Form):
    date = VendDateTimeField(required=False)

class VendDateTimeFieldTestCase(TestCase):

    required_msg = str(VendDateTimeField().error_messages['required'])
    invalid_msg = str(VendDateTimeField().error_messages['invalid'])

    def test_inputs_to_expected_outputs(self):
        valid_inputs = [
            "2014-07-01T20:22:58+00:00",
            "1900-07-01T20:22:58-05:00",
        ]
        valid = {v: parse_datetime(v) for v in valid_inputs}

        invalid = {
            "a": [self.invalid_msg],
            "1": [self.invalid_msg],
        }

        self.assertFieldOutput(
            VendDateTimeField,
            valid=valid,
            invalid=invalid,
            empty_value=None,
        )

    def test_null_date_required(self):
        form = VendDateTimeForm({'date': 'null'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form['date'].errors, [self.required_msg])

    def test_null_date_not_required(self):
        form = VendOptionalDateTimeForm({'date': 'null'})
        self.assertTrue(form.is_valid())
