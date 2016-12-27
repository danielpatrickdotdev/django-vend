from django.db import models

import requests

from django_vend.core.exceptions import VendSyncError


class VendAPIManagerMixin(object):

    def value_or_error(self, dict_obj, key, e=KeyError):
        value = dict_obj.get(key)
        if not value:
            raise e('dict_obj does not contain key {}'.format(key))

        return value

    def retrieve_from_api(self, retailer, url):
        headers = {
            'Authorization': 'Bearer {}'.format(retailer.access_token),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        try:
            result = requests.get(url, headers=headers)
        except requests.exceptions.RequestException as e:
            raise VendSyncError(e)
        if result.status_code != requests.codes.ok:
            raise VendSyncError(
                'Received {} status from Vend API'.format(result.status_code))
        try:
            data = result.json()
        except ValueError as e:
            raise VendSyncError(e)
        return data

    def get_inner_json(self, obj, container_name):
        inner = None
        if container_name is not None:
            try:
                inner = obj[container_name]
            except KeyError as e:
                raise VendSyncError(e)
        return inner or obj


class VendAPISingleObjectManagerMixin(VendAPIManagerMixin):

    resource_object_url = None
    json_object_name = None

    def retrieve_object_from_api(self, retailer, object_id, defaults=None):
        # Call API
        url = self.resource_object_url.format(retailer.name, object_id)
        data = self.retrieve_from_api(retailer, url)

        data = self.get_inner_json(data, self.json_object_name)

        return self.parse_object(retailer, data, defaults)

    def parse_object(self, retailer, result, defaults=None):
        raise NotImplementedError('parse_object method must be implemented '
                                  'by {}'.format(self.__class__.__name__))


class VendAPICollectionManagerMixin(VendAPIManagerMixin):

    resource_collection_url = None
    json_collection_name = None

    def retrieve_collection_from_api(self, retailer):
        # Call API
        url = self.resource_collection_url.format(retailer.name)
        data = self.retrieve_from_api(retailer, url)

        data = self.get_inner_json(data, self.json_collection_name)

        # Save to DB & Return saved objects
        return self.parse_collection(retailer, data)

    def parse_collection(self, retailer, result):
        raise NotImplementedError('parse_collection method must be implemented '
                                  'by {}'.format(self.__class__.__name__))

class BaseVendAPIManager(models.Manager,
                         VendAPICollectionManagerMixin,
                         VendAPISingleObjectManagerMixin):
    """
    Simple implementation of a Manager class for a django model that contains
    data retrieved from the Vend API. It may be that due to the inconsistencies
    of the API, this class is never actually used; Managers may have to
    implement custom logic for individual objects.
    """
    def parse_collection(self, retailer, result):
        objects = []
        e = VendSyncError

        for object_stub in result:
            id = self.value_or_error(object_stub, 'id', e)
            objects.append(self.retrieve_object_from_api(retailer, id))

        return objects
