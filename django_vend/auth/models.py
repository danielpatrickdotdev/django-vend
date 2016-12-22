from django.db import models
from django.conf import settings

from dateutil.parser import parse as date_parse

from django_vend.core.managers import BaseVendAPIManager

class VendUserManager(BaseVendAPIManager):

    resource_collection_url = 'https://{}.vendhq.com/api/users'
    resource_object_url = 'https://{}.vendhq.com/api/1.0/user/{}'

    json_collection_name = 'users'

    def get_account_type(self, account_type_str, e=Exception):
        try:
            initial = account_type_str[0].upper()
        except IndexError:
            raise e
        choices = [c[0] for c in self.model.ACCOUNT_TYPE_CHOICES]
        if not initial in choices:
            raise e
        return initial

    def parse_object(self, retailer, result, override_defaults):
        e = Exception #TODO: Decide appropriate exception
        uid = self.value_or_error(result, 'id', e)
        name = self.value_or_error(result, 'name', e)
        display_name = self.value_or_error(result, 'display_name', e)
        email = self.value_or_error(result, 'email', e)
        created_at = date_parse(self.value_or_error(result, 'created_at', e))
        updated_at = date_parse(self.value_or_error(result, 'updated_at', e))
        defaults = {
            'retailer': retailer,
            'name': name,
            'display_name': display_name,
            'email': email,
            'created_at': created_at,
            'updated_at': updated_at,
        }
        if 'image' in result:
            image = self.value_or_error(result['image'], 'url', e)
            defaults['image'] = image

        for key in override_defaults:
            defaults[key] = override_defaults[key]

        user, created = self.update_or_create(uid=uid, defaults=defaults)
        return user

    def parse_collection(self, retailer, result):
        users = []
        e = Exception #TODO: decide appropriate exception class

        for user in result:
            id = self.value_or_error(user, 'id', e)
            account_type_str = self.value_or_error(user, 'account_type', e)
            account_type = self.get_account_type(account_type_str)
            users.append(self.retrieve_object_from_api(
                retailer, id, defaults={'account_type': account_type}))

        return users


class VendRetailer(models.Model):
    name = models.CharField(unique=True, max_length=256)
    access_token = models.CharField(max_length=256)
    expires = models.DateTimeField()
    expires_in = models.IntegerField()
    refresh_token = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class VendUser(models.Model):
    ADMIN = 'A'
    MANAGER = 'M'
    CASHIER = 'C'
    ACCOUNT_TYPE_CHOICES = (
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (CASHIER, 'Cashier'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL)
    uid = models.UUIDField(editable=False)
    retailer = models.ForeignKey(VendRetailer, editable=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    display_name = models.CharField(max_length=256)
    email = models.EmailField()
    image = models.URLField(blank=True)
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
