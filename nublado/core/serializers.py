import json
import uuid


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # if the obj is uuid, return the value of uuid
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class BaseSerializer(object):
    # Data fields to be returned in get_minimal_data()
    minimal_data_fields = []
    json_encoder = json.JSONEncoder

    def json_data(self):
        return json.dumps(self.data, cls=self.json_encoder)

    def get_minimal_data(self):
        """
        Returns a dict of values specified in minimal_data_fields.
        """

        minimal_data = {}
        for field in self.minimal_data_fields:
            minimal_data[field] = self.data[field]
        return minimal_data
