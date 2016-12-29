import re

from django import forms
from django.utils.dateparse import parse_datetime
from django.core.exceptions import ValidationError

def valid_date(date):
    regex = ("^(?:[1-9]\d{3}-(?:(?:0[1-9]|1[0-2])-(?:0[1-9]|1\d|2[0-8])|(?:0[13"
             "-9]|1[0-2])-(?:29|30)|(?:0[13578]|1[02])-31)|(?:[1-9]\d(?:0[48]|["
             "2468][048]|[13579][26])|(?:[2468][048]|[13579][26])00)-02-29)T(?:"
             "[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:Z|[+-][01]\d:[0-5]\d)$")
    return re.search(regex, date)

class VendDateTimeField(forms.DateTimeField):
    def to_python(self, value):
        if value not in self.empty_values and valid_date(value):
            try:
                value = parse_datetime(value)
            except ValueError:
                pass
        return super(VendDateTimeField, self).to_python(value)
