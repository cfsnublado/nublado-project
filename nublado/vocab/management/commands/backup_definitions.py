import getpass

import requests
from rest_framework import status

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.management.base import BaseCommand, CommandError

from vocab.models import VocabDefinition, VocabEntry


class Command(BaseCommand):
    help = 'Backs up definitions.'
    OXFORD_API_ID = getattr(settings, 'OXFORD_API_ID', None)
    OXFORD_API_KEY = getattr(settings, 'OXFORD_API_KEY', None)
    lexical_categories = {
        'noun': VocabDefinition.NOUN,
        'adjective': VocabDefinition.ADJECTIVE,
        'adverb': VocabDefinition.ADVERB,
        'verb': VocabDefinition.VERB,
        'expression': VocabDefinition.EXPRESSION,
        'other': VocabDefinition.OTHER
    }

    def login_user(self):
        username = input('Username: ')
        password = getpass.getpass('Password: ')

        user = authenticate(username=username, password=password)

        if user is not None:
            if not user.is_superuser:
                raise CommandError('Must be superuser')
        else:
            raise CommandError('Invalid login')

    def add_definitions_from_oxford(self, json_data, vocab_entry):
        '''
        json_data: The json returned from the Oxford api for a vocab entry.
        '''
        for result in json_data['results']:
            for lexical_entry in result['lexicalEntries']:
                lexical_category = lexical_entry['lexicalCategory'].lower()

                if 'derivativeOf' in lexical_entry:
                    print('Derived from:')
                    for derived_from in lexical_entry['derivativeOf']:
                        print(derived_from['id'])
                else:
                    for entry in lexical_entry['entries']:
                        if 'senses' in entry:
                            for sense in entry['senses']:
                                if 'definitions' in sense:
                                    for definition in sense['definitions']:
                                        if lexical_category not in self.lexical_categories:
                                            lexical_category = 'other'
                                        VocabDefinition.objects.create(
                                            vocab_entry=vocab_entry,
                                            definition_type=self.lexical_categories[lexical_category],
                                            definition=definition
                                        )
                                        print(lexical_category + ": " + definition)

    def add_arguments(self, parser):
        parser.add_argument('--output_path', nargs=1, type=str)

    def handle(self, *args, **options):
        self.login_user()

        oxford_entry_url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/{0}/{1}'
        headers = {
            'Accept': 'application/json',
            'app_id': self.OXFORD_API_ID,
            'app_key': self.OXFORD_API_KEY
        }
        vocab_entries = VocabEntry.objects.filter(language='en')

        for vocab_entry in vocab_entries:
            self.stdout.write(self.style.SUCCESS(vocab_entry))

            if not VocabDefinition.objects.filter(vocab_entry=vocab_entry).exists():
                url = oxford_entry_url.format(
                    vocab_entry.language,
                    vocab_entry.entry
                )
                response = requests.get(url, headers=headers)
                if response.status_code == status.HTTP_200_OK:
                    response_json = response.json()
                    self.add_definitions_from_oxford(response_json, vocab_entry)
