from django.db import models
from django.utils import timezone
from django.urls import reverse

from django_vend.core.managers import BaseVendAPIManager
from django_vend.core.exceptions import VendSyncError
from django_vend.core.utils import parse_date
from django_vend.auth.models import VendRetailer


class VendOutletManager(BaseVendAPIManager):

    resource_collection_url = 'https://{}.vendhq.com/api/2.0/outlets'
    resource_object_url = 'https://{}.vendhq.com/api/2.0/outlets/{}'

    json_collection_name = 'data'
    json_object_name = 'data'

    def parse_json_object(self, json_obj):
        obj = {
            'name': self.get_dict_value(json_obj, 'name'),
            'time_zone': self.get_dict_value(json_obj, 'time_zone'),
            'currency': self.get_dict_value(json_obj, 'currency'),
            'currency_symbol': self.get_dict_value(json_obj, 'currency_symbol'),
            'deleted_at': parse_date(self.get_dict_value(
                                json_obj, 'deleted_at', required=False)),
        }

        inclusive = self.get_dict_value(json_obj, 'display_prices')
        obj['display_prices_tax_inclusive'] = (inclusive == 'inclusive')

        return obj

class VendRegisterManager(BaseVendAPIManager):

    resource_collection_url = 'https://{}.vendhq.com/api/2.0/registers'
    resource_object_url = 'https://{}.vendhq.com/api/2.0/registers/{}'

    json_collection_name = 'data'
    json_object_name = 'data'

    def synchronise(self, retailer, *args, **kwargs):
        VendOutlet.objects.synchronise(retailer)
        super(VendRegisterManager, self).synchronise(retailer, *args, **kwargs)

    def parse_json_object(self, json_obj):
        outlet_id = self.get_dict_value(json_obj, 'outlet_id')
        try:
            outlet = VendOutlet.objects.get(uid=outlet_id)
        except VendOutlet.DoesNotExist:
            raise self.sync_exception('Invalid uid {} for VendOutlet'.format(
                outlet_id))

        obj = {
            'name': self.get_dict_value(json_obj, 'name'),
            'outlet': outlet,
            'invoice_prefix': self.get_dict_value(
                                json_obj, 'invoice_prefix', required=False),
            'invoice_suffix': self.get_dict_value(
                                json_obj, 'invoice_suffix', required=False),
            'invoice_sequence': self.get_dict_value(
                                            json_obj, 'invoice_sequence'),
            'deleted_at': parse_date(self.get_dict_value(
                                json_obj, 'deleted_at', required=False)),
            'is_open': self.get_dict_value(json_obj, 'is_open'),
            'register_open_time': parse_date(self.get_dict_value(
                            json_obj, 'register_open_time', required=False)),
            'register_close_time': parse_date(self.get_dict_value(
                            json_obj, 'register_close_time', required=False)),
        }
        return obj

class VendOutlet(models.Model):
    # /api/outlets AND /api/2.0/outlets
    uid = models.UUIDField(editable=False)
    name = models.CharField(max_length=256)
    # /api/outlets
    #email = models.EmailField()
    #address1 = models.CharField(max_length=256)
    #address2 = models.CharField(max_length=256)
    #city = models.CharField(max_length=256)
    #country = models.CharField(max_length=256)
    #postcode = models.CharField(max_length=256)
    #state = models.CharField(max_length=256)
    #suburb = models.CharField(max_length=256)
    retailer = models.ForeignKey(VendRetailer, editable=False,
        on_delete=models.CASCADE)
    # /api/outlets AND /api/2.0/outlets
    time_zone = models.CharField(max_length=256)
    # /api/2.0/outlets
    currency = models.CharField(max_length=256)
    currency_symbol = models.CharField(max_length=32)
    display_prices_tax_inclusive = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True)

    objects = VendOutletManager()

    def get_absolute_url(self):
        return reverse('vend_outlet_detail', args=[str(self.uid)])

    def __str__(self):
        return self.name

class VendRegister(models.Model):
    # /api/registers AND /api/2.0/registers
    uid = models.UUIDField(editable=False)
    name = models.CharField(max_length=256)
    outlet = models.ForeignKey(VendOutlet, editable=False,
        on_delete=models.CASCADE)
    invoice_prefix = models.CharField(max_length=32)
    invoice_suffix = models.CharField(max_length=32)
    invoice_sequence = models.PositiveIntegerField()
    # /api/registers
    #register_open_count_sequence = models.PositiveIntegerField(null=True)
    # /api/2.0/registers
    deleted_at = models.DateTimeField(null=True)
    is_open = models.BooleanField(default=False)
    # /api/registers AND /api/2.0/registers
    register_open_time = models.DateTimeField(blank=True, null=True)
    register_close_time = models.DateTimeField(blank=True, null=True)
    # Non-API
    retailer = models.ForeignKey(VendRetailer, editable=False,
        on_delete=models.CASCADE)

    objects = VendRegisterManager()

    def __str__(self):
        return self.name
