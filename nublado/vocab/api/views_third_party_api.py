import requests
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.views_api import APIDefaultsMixin
from ..conf import settings
from .permissions import IsSuperuser

OXFORD_API_ID = getattr(settings, 'OXFORD_API_ID', None)
OXFORD_API_KEY = getattr(settings, 'OXFORD_API_KEY', None)


def get_oxford_entry_data(json_data):
    '''
    json_data: The json returned from the Oxford api for a vocab entry.
    '''
    for result in json_data['results']:
        for lexical_entry in result['lexicalEntries']:
            lexical_category = lexical_entry['lexicalCategory']

            if 'derivativeOf' in lexical_entry:
                print('Derived from:')
                for derived_from in lexical_entry['derivativeOf']:
                    print(derived_from['id'])
            else:
                for entry in lexical_entry['entries']:
                    if 'senses' in entry:
                        for sense in entry['senses']:
                            for definition in sense['definitions']:
                                print(lexical_category + ": " + definition)


class OxfordAPIEntryView(APIDefaultsMixin, APIView):
    permission_classes = (
        IsAuthenticated,
        IsSuperuser
    )
    oxford_entry_url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/{0}/{1}/regions={2}'

    def get(self, request, *args, **kwargs):
        language = request.query_params.get('language', 'en')
        entry = request.query_params.get('entry', None)
        region = request.query_params.get('region', 'us')
        headers = {
            'Accept': 'application/json',
            'app_id': OXFORD_API_ID,
            'app_key': OXFORD_API_KEY
        }
        url = self.oxford_entry_url.format(language, entry, region)
        response = requests.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            response_json = response.json()
            get_oxford_entry_data(response_json)
            return Response(data=response_json, content_type='application/json')
        else:
            return Response(data={}, status=response.status_code)
