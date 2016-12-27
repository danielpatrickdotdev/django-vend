from django.db import models
from django.conf import settings
from django.utils import timezone

from dateutil.parser import parse as date_parse

from django_vend.core.managers import BaseVendAPIManager
from django_vend.core.utils import get_vend_setting
from django_vend.core.exceptions import VendSyncError

DEFAULT_USER_IMAGE = get_vend_setting('VEND_DEFAULT_USER_IMAGE')

class VendUserManager(BaseVendAPIManager):

    resource_collection_url = 'https://{}.vendhq.com/api/users'
    resource_object_url = 'https://{}.vendhq.com/api/1.0/user/{}'

    json_collection_name = 'users'

    def get_account_type(self, account_type_str, exception=Exception):
        try:
            initial = account_type_str[0].upper()
        except IndexError as e:
            raise exception(e)
        choices = [c[0] for c in self.model.ACCOUNT_TYPE_CHOICES]
        if not initial in choices:
            raise exception(e)
        return initial

    def parse_json_object(self, json_obj):
        uid = self.value_or_error(json_obj, 'id')
        name = self.value_or_error(json_obj, 'name')
        display_name = self.value_or_error(json_obj, 'display_name')
        email = self.value_or_error(json_obj, 'email')
        created_at = date_parse(self.value_or_error(json_obj, 'created_at'))
        updated_at = date_parse(self.value_or_error(json_obj, 'updated_at'))
        obj = {
            'name': name,
            'display_name': display_name,
            'email': email,
            'created_at': timezone.make_aware(created_at, timezone.utc),
            'updated_at': timezone.make_aware(updated_at, timezone.utc),
        }
        if 'image' in json_obj:
            image = self.value_or_error(json_obj['image'], 'url')
            obj['image'] = image

        return obj

    def parse_collection(self, retailer, result):
        created = False

        for object_stub in result:
            pk = self.value_or_error(object_stub, 'id')
            defaults = self.parse_json_collection_object(object_stub)
            created = created or self._retrieve_object_from_api(
                retailer, pk, defaults=defaults)

        return created

    def parse_json_collection_object(self, json_obj):
        account_type_str = self.value_or_error(json_obj, 'account_type')
        account_type = self.get_account_type(account_type_str)
        return {'account_type': account_type}


class VendRetailer(models.Model):
    name = models.CharField(unique=True, max_length=256)
    access_token = models.CharField(max_length=256)
    expires = models.DateTimeField()
    expires_in = models.IntegerField()
    refresh_token = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class VendProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='vendprofile',
        on_delete=models.CASCADE)
    retailer = models.ForeignKey(
        VendRetailer,
        related_name='vendprofile',
        on_delete=models.CASCADE)
    vendusers = models.ManyToManyField(
        'VendUser',
        related_name='vendprofiles')

class VendUser(models.Model):
    ADMIN = 'A'
    MANAGER = 'M'
    CASHIER = 'C'
    ACCOUNT_TYPE_CHOICES = (
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (CASHIER, 'Cashier'),
    )

    uid = models.UUIDField(editable=False)
    retailer = models.ForeignKey(VendRetailer, editable=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    display_name = models.CharField(max_length=256)
    email = models.EmailField()
    image = models.URLField(blank=True, default=DEFAULT_USER_IMAGE)
    account_type = models.CharField(
        max_length=1,
        choices=ACCOUNT_TYPE_CHOICES,
        default=CASHIER,
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    objects = VendUserManager()

    def __str__(self):
        return self.name
