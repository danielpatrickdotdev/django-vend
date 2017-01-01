from django import forms

from django_vend.core.forms import VendDateTimeField
from .models import VendOutlet, VendRegister


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

            if 'instance' not in kwargs or kwargs['instance'] is None:
                # Note: currently assumes instance is only ever passed as a
                # kwarg and not an arg - need to check but this is probably bad
                try:
                    kwargs['instance'] = VendOutlet.objects.get(uid=uid)
                except VendOutlet.DoesNotExist:
                    pass

        super(VendOutletForm, self).__init__(data, *args, **kwargs)

    class Meta:
        model = VendOutlet
        fields = ['uid', 'name', 'time_zone', 'currency', 'currency_symbol',
                  'display_prices_tax_inclusive', 'deleted_at']


class VendRegisterForm(forms.ModelForm):

    deleted_at = VendDateTimeField(required=False)
    register_open_time = VendDateTimeField(required=False)
    register_close_time = VendDateTimeField(required=False)

    def __init__(self, data=None, *args, **kwargs):
        if data:
            uid = data.pop('id', None)
            if uid is not None:
                data['uid'] = uid

            outlet_id = data.pop('outlet_id', None)
            if outlet_id is not None:
                try:
                    data['outlet'] = VendOutlet.objects.get(uid=outlet_id).pk
                except VendOutlet.DoesNotExist:
                    outlet = None

            deleted_at = data.get('deleted_at')
            if deleted_at is not None and deleted_at == 'null':
                data['deleted_at'] = None

            if 'instance' not in kwargs or kwargs['instance'] is None:
                # Note: currently assumes instance is only ever passed as a
                # kwarg and not an arg - need to check but this is probably bad
                try:
                    kwargs['instance'] = VendRegister.objects.get(uid=uid)
                except VendRegister.DoesNotExist:
                    pass

        super(VendRegisterForm, self).__init__(data, *args, **kwargs)

    class Meta:
        model = VendRegister
        fields = ['uid', 'name', 'outlet', 'invoice_prefix', 'invoice_suffix',
                  'invoice_sequence', 'deleted_at', 'is_open',
                  'register_open_time', 'register_close_time']
