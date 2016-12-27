from django.db import models

import requests

from django_vend.core.exceptions import VendSyncError


class AbstractVendAPIManager(models.Manager):
    def synchronise(self, retailer, object_id=None):
        if object_id:
            return self._retrieve_object_from_api(retailer, object_id)
        else:
            return self._retrieve_collection_from_api(retailer)

class VendAPIManagerMixin(object):

    sync_exception = VendSyncError

    def value_or_error(self, dict_obj, key, exception=None):
        if exception is None:
            exception = self.sync_exception
        value = dict_obj.get(key)
        if not value:
            raise exception('dict_obj does not contain key {}'.format(key))

        return value

    def _retrieve_from_api(self, retailer, url):
        headers = {
            'Authorization': 'Bearer {}'.format(retailer.access_token),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        try:
            result = requests.get(url, headers=headers)
        except requests.exceptions.RequestException as e:
            raise self.sync_exception(e)
        if result.status_code != requests.codes.ok:
            raise self.sync_exception(
                'Received {} status from Vend API'.format(result.status_code))
        try:
            data = result.json()
        except ValueError as e:
            raise self.sync_exception(e)
        return data

    def get_inner_json(self, obj, container_name):
        inner = None
        if container_name is not None:
            try:
                inner = obj[container_name]
            except KeyError as e:
                raise self.sync_exception(e)
        return inner or obj


class VendAPISingleObjectManagerMixin(VendAPIManagerMixin):

    resource_object_url = None
    json_object_name = None

    def _retrieve_object_from_api(self, retailer, object_id, defaults=None):
        # Call API
        url = self.resource_object_url.format(retailer.name, object_id)
        data = self._retrieve_from_api(retailer, url)

        data = self.get_inner_json(data, self.json_object_name)

        return self.parse_object(retailer, data, defaults)

    def parse_json_object(self, json_obj):
        raise NotImplementedError('parse_json_object method must be '
                                  'implemented by {}'.format(
                                      self.__class__.__name__))

    def parse_object(self, retailer, result, additional_defaults=None):
        uid = self.value_or_error(result, 'id')
        defaults = self.parse_json_object(result)
        defaults['retailer'] = retailer

        for key in additional_defaults:
            defaults[key] = additional_defaults[key]

        obj, created = self.update_or_create(uid=uid, defaults=defaults)
        return created

class VendAPICollectionManagerMixin(VendAPIManagerMixin):

    resource_collection_url = None
    json_collection_name = None

    def _retrieve_collection_from_api(self, retailer):
        # Call API
        url = self.resource_collection_url.format(retailer.name)
        data = self._retrieve_from_api(retailer, url)

        data = self.get_inner_json(data, self.json_collection_name)

        # Save to DB & Return saved objects
        return self.parse_collection(retailer, data)

    def parse_json_collection_object(self, json_obj):
        return {}

    def parse_collection(self, retailer, result):
        created = False

        for object_stub in result:
            pk = self.value_or_error(object_stub, 'id')
            defaults = self.parse_json_collection_object(object_stub)
            created = created or self._retrieve_object_from_api(
                retailer, pk, defaults=defaults)

        return created

class BaseVendAPIManager(AbstractVendAPIManager,
                         VendAPICollectionManagerMixin,
                         VendAPISingleObjectManagerMixin):
    """
    Simple implementation of a Manager class for a django model that contains
    data retrieved from the Vend API.
    """
    pass
