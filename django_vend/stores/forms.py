from django import forms

from django_vend.core.forms import VendDateTimeField
from .models import VendOutlet


class VendOutletForm(forms.ModelForm):

    deleted_at = VendDateTimeField(required=False)

    def __init__(self, data=None, *args, **kwargs):
        if data:
            uid = data.pop('id', None)
            if uid is not None:
                data['uid'] = uid

            tax_inc = data.pop('display_prices', None)
            if tax_inc is not None:
                if tax_inc == 'inclusive':
                    data['display_prices_tax_inclusive'] = True
                elif tax_inc == 'exclusive':
                    data['display_prices_tax_inclusive'] = False

            deleted_at = data.get('deleted_at')
            if deleted_at is not None and deleted_at == 'null':
                data['deleted_at'] = None

        super(VendOutletForm, self).__init__(data, *args, **kwargs)

    class Meta:
        model = VendOutlet
        fields = ['uid', 'name', 'time_zone', 'currency', 'currency_symbol',
                  'display_prices_tax_inclusive', 'deleted_at']
