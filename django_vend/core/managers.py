from django.db import models

import requests


class BaseVendAPIManager(models.Manager):

    resource_collection_url = None
    resource_object_url = None
    json_collection_name = None
    json_object_name = None

    def value_or_error(self, dict_obj, key, e=KeyError):
        value = dict_obj.get(key)
        if not value:
            raise e

        return value

    def retrieve_from_api(self, retailer, url):
        headers = {
            'Authorization': 'Bearer {}'.format(retailer.access_token),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        result = requests.get(url, headers=headers)
        try:
            data = result.json()
        except ValueError:
            #TODO: decide what to do here!
            data = None
        return data

    def get_inner_json(self, obj, container_name):
        inner = None
        if container_name is not None:
            try:
                inner = obj[container_name]
            except KeyError:
                #TODO: decide what to do here!
                pass
        return inner or obj

    def retrieve_object_from_api(self, retailer, object_id, defaults=None):
        # Call API
        url = self.resource_object_url.format(retailer.name, object_id)
        data = self.retrieve_from_api(retailer, url)

        data = self.get_inner_json(data, self.json_object_name)

        return self.parse_object(retailer, data, defaults)

    def retrieve_collection_from_api(self, retailer):
        # Call API
        url = self.resource_collection_url.format(retailer.name)
        data = self.retrieve_from_api(retailer, url)

        data = self.get_inner_json(data, self.json_collection_name)

        # Save to DB & Return saved objects
        return self.parse_collection(retailer, data)

    def parse_object(self, retailer, result, defaults=None):
        raise NotImplementedError('parse_object method must be implemented '
                                  'by {}'.format(self.__class__.__name__))

    def parse_collection(self, retailer, result):
        objects = []
        e = Exception #TODO: decide appropriate exception class

        for object_stub in result:
            id = self.value_or_error(object_stub, 'id', e)
            objects.append(self.retrieve_object_from_api(retailer, id))

        return objects
