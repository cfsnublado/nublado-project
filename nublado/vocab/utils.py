import requests
from jsonschema import validate as validate_schema

from rest_framework import status

from django.contrib.auth import get_user_model

from .conf import settings
from .models import (
    VocabContextEntry, VocabDefinition, VocabEntry,
    VocabEntryJsonData, VocabProject, VocabSource
)
from .serializers import (
    VocabDefinitionSerializer, VocabEntrySerializer,
    VocabContextSerializer, VocabProjectSerializer,
    VocabSourceSerializer
)

User = get_user_model()


def export_vocab_entries(request=None, language=None):
    '''
    Generates a serialized backup of vocab entries.
    '''
    vocab_entries_dict = {}
    qs = VocabEntry.objects

    if language and language in settings.LANGUAGES_DICT:
        qs = qs.filter(language=language)

    vocab_entries_dict['vocab_entries'] = []

    for vocab_entry in qs.all():
        vocab_entry_dict = {}
        vocab_entry_serializer = VocabEntrySerializer(
            vocab_entry,
            context={'request': request},
        )
        vocab_entry_dict['vocab_entry_data'] = vocab_entry_serializer.get_minimal_data()

        if vocab_entry.vocab_definitions.count():
            vocab_entry_dict['vocab_definitions'] = []
            for vocab_definition in vocab_entry.vocab_definitions.all():
                vocab_definition_dict = {}
                vocab_definition_serializer = VocabDefinitionSerializer(
                    vocab_definition,
                    context={'request': request}
                )
                vocab_definition_dict['vocab_definition_data'] = vocab_definition_serializer.get_minimal_data()
                vocab_entry_dict['vocab_definitions'].append(vocab_definition_dict)

        vocab_entries_dict['vocab_entries'].append(vocab_entry_dict)

    return vocab_entries_dict


def export_vocab_source(request=None, vocab_source=None):
    '''
    Generates a serialized backup of a vocab source.
    '''
    if vocab_source:
        vocab_project_serializer = VocabProjectSerializer(
            vocab_source.vocab_project,
            context={'request': request}
        )
        vocab_source_serializer = VocabSourceSerializer(
            vocab_source,
            context={'request': request}
        )
        vocab_source_dict = {
            'vocab_project_data': vocab_project_serializer.get_minimal_data(),
            'vocab_source_data': vocab_source_serializer.get_minimal_data()
        }

        if vocab_source.vocab_contexts.count():
            vocab_source_dict['vocab_contexts'] = []

            for vocab_context in vocab_source.vocab_contexts.all():
                vocab_context_serializer = VocabContextSerializer(
                    vocab_context,
                    context={'request': request}
                )
                vocab_context_dict = {
                    'vocab_context_data': vocab_context_serializer.get_minimal_data(),
                }

                if vocab_context.vocabcontextentry_set.count():
                    vocab_context_dict['vocab_entries'] = []
                    for vocab_context_entry in vocab_context.vocabcontextentry_set.all():
                        vocab_entry = vocab_context_entry.vocab_entry
                        vocab_entry_serializer = VocabEntrySerializer(
                            vocab_entry,
                            context={'request': request}
                        )
                        vocab_context_dict['vocab_entries'].append(
                            {
                                'vocab_entry_data': vocab_entry_serializer.get_minimal_data(),
                                'vocab_entry_tags': vocab_context_entry.get_vocab_entry_tags()
                            }
                        )

                vocab_source_dict['vocab_contexts'].append(vocab_context_dict)

        return vocab_source_dict


def import_vocab_entries(data):
    '''
    Deserialzes data from vocab entries backup. (See export_vocab_entries)
    '''
    validate_vocab_entries_json_schema(data)

    for vocab_entry_dict in data['vocab_entries']:
        vocab_entry_data = vocab_entry_dict['vocab_entry_data']

        if not VocabEntry.objects.filter(
            entry=vocab_entry_data['entry'],
            language=vocab_entry_data['language']
        ).exists():
            vocab_entry = VocabEntry.objects.create(
                **vocab_entry_data
            )
            if 'vocab_definitions' in vocab_entry_dict:
                for vocab_definition in vocab_entry_dict['vocab_definitions']:
                    vocab_definition_data = vocab_definition['vocab_definition_data']
                    VocabDefinition.objects.create(
                        vocab_entry_id=vocab_entry.id,
                        **vocab_definition_data
                    )


def import_vocab_source(data, creator):
    '''
    data: Serialized json data from vocab source backup.
    '''
    validate_vocab_source_json_schema(data)

    creator_id = creator.id
    VocabSource.objects.filter(
        creator_id=creator_id,
        name=data['vocab_source_data']['name']
    ).delete()
    vocab_source_data = data['vocab_source_data']
    vocab_project_data = data['vocab_project_data']
    vocab_source_serializer = VocabSourceSerializer(
        data=vocab_source_data
    )
    vocab_source_serializer.is_valid(raise_exception=True)

    try:
        vocab_project = VocabProject.objects.get(
            name=vocab_project_data['name']
        )
    except VocabProject.DoesNotExist:
        vocab_project = VocabProject.objects.create(
            owner_id=creator_id,
            **vocab_project_data
        )

    vocab_source = vocab_source_serializer.save(
        creator_id=creator_id,
        vocab_project_id=vocab_project.id
    )

    if 'vocab_contexts' in data:

        for vocab_context_dict in data['vocab_contexts']:
            vocab_context_data = vocab_context_dict['vocab_context_data']
            vocab_context_serializer = VocabContextSerializer(
                data=vocab_context_data
            )
            vocab_context_serializer.is_valid(raise_exception=True)
            vocab_context = vocab_context_serializer.save(
                vocab_source_id=vocab_source.id
            )

            if 'vocab_entries' in vocab_context_dict:

                for vocab_context_entry_dict in vocab_context_dict['vocab_entries']:
                    vocab_entry_data = vocab_context_entry_dict['vocab_entry_data']

                    try:
                        vocab_entry = VocabEntry.objects.get(
                            entry=vocab_entry_data['entry'],
                            language=vocab_entry_data['language']
                        )
                    except VocabEntry.DoesNotExist:
                        vocab_entry = VocabEntry.objects.create(
                            **vocab_entry_data
                        )

                    vocab_context_entry = VocabContextEntry.objects.create(
                        vocab_entry_id=vocab_entry.id,
                        vocab_context_id=vocab_context.id
                    )

                    if 'vocab_entry_tags' in vocab_context_entry_dict:
                        for vocab_entry_tag in vocab_context_entry_dict['vocab_entry_tags']:
                            vocab_context_entry.add_vocab_entry_tag(vocab_entry_tag)
                        vocab_context_entry.save()


def validate_vocab_entries_json_schema(data):
    schema = {
        'type': 'object',
        'properties': {
            'vocab_entries': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'vocab_entry_data': {
                            'type': 'object',
                            'properties': {
                                'language': {
                                    'type': 'string',
                                    'minLength': 2,
                                    'maxLength': 2,
                                },
                                'entry': {
                                    'type': 'string'
                                },
                                'pronunciation_spelling': {
                                    'type': 'string',
                                    'blank': True
                                },
                                'pronunciation_ipa': {
                                    'type': 'string',
                                    'blank': True
                                },
                                'description': {
                                    'type': 'string',
                                    'blank': True
                                },
                                'date_created': {
                                    'type': 'string'
                                }
                            },
                            'required': ['entry']
                        },
                    },
                    'required': ['vocab_entry_data'],
                },
            },
        },
        'required': ['vocab_entries'],
    }
    validate_schema(data, schema)


def validate_vocab_source_json_schema(data):
    schema = {
        'type': 'object',
        'properties': {
            'vocab_project_data': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string'
                    }
                },
                'required': ['name']
            },
            'vocab_source_data': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                    },
                    'description': {
                        'type': 'string',
                        'blank': True,
                    },
                    'source_type': {
                        'type': 'integer',
                    },
                    'date_created': {
                        'type': 'string'
                    }
                },
                'required': ['name'],
            },
            'vocab_contexts': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'vocab_context_data': {
                            'type': 'object',
                            'properties': {
                                'content': {
                                    'type': 'string'
                                },
                                'date_created': {
                                    'type': 'string'
                                }
                            },
                            'required': ['content'],
                        },
                        'vocab_entries': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'vocab_entry_data': {
                                        'type': 'object',
                                        'properties': {
                                            'language': {
                                                'type': 'string',
                                                'minLength': 2,
                                                'maxLength': 2
                                            },
                                            'entry': {
                                                'type': 'string',
                                            },
                                            'pronunciation_ipa': {
                                                'type': 'string',
                                                'blank': True
                                            },
                                            'pronunciation_spelling': {
                                                'type': 'string',
                                                'blank': True
                                            },
                                            'date_created': {
                                                'type': 'string'
                                            }
                                        },
                                        'required': ['entry'],
                                    },
                                    'vocab_entry_tags': {
                                        'type': 'array',
                                        'items': {
                                            'type': 'string'
                                        }
                                    }
                                },
                                'required': ['vocab_entry_data', 'vocab_entry_tags']
                            },
                        },
                    },
                    'required': ['vocab_context_data']
                },
            },
        },
        'required': ['vocab_source_data']
    }
    validate_schema(data, schema)


# Oxford API stuff
def get_oxford_entry_json(api_id, api_key, vocab_entry):
    '''
    api_id: Oxford api id
    api_key: Oxford api key
    vocab_entry: A VocabEntry object
    '''

    oxford_entry_url = 'https://od-api.oxforddictionaries.com/api/v1/entries/{language}/{entry}'.format(
        language=vocab_entry.language,
        entry=vocab_entry.entry
    )

    if vocab_entry.language == 'en':
        oxford_entry_url = oxford_entry_url + '/regions=us'

    response = requests.get(
        oxford_entry_url,
        headers={
            'Accept': 'application/json',
            'app_id': api_id,
            'app_key': api_key
        }
    )

    if response.status_code == status.HTTP_200_OK:
        response_json = response.json()
        VocabEntryJsonData.objects.create(
            vocab_entry=vocab_entry,
            json_data=response_json,
            json_data_source=VocabEntryJsonData.OXFORD
        )
        add_definitions_from_oxford(response_json, vocab_entry)


def add_definitions_from_oxford(json_data, vocab_entry):
    '''
    json_data: The json returned from the Oxford api for a vocab entry.
    vocab_entry: A VocabEntry object
    '''

    lexical_categories = {
        'noun': VocabDefinition.NOUN,
        'adjective': VocabDefinition.ADJECTIVE,
        'adverb': VocabDefinition.ADVERB,
        'verb': VocabDefinition.VERB,
        'idiomatic': VocabDefinition.EXPRESSION,
        'other': VocabDefinition.OTHER
    }

    for result in json_data['results']:
        if 'lexicalEntries' in result:
            for lexical_entry in result['lexicalEntries']:
                lexical_category = lexical_entry['lexicalCategory'].lower()

                # Add pronunciations
                if 'pronunciations' in lexical_entry:
                    for pronunciation in lexical_entry['pronunciations']:
                        if 'phoneticNotation' in pronunciation:
                            if pronunciation['phoneticNotation'].lower() == 'ipa':
                                if 'phoneticSpelling' in pronunciation:
                                    vocab_entry.pronunciation_ipa = pronunciation['phoneticSpelling']
                                    vocab_entry.save()

                # Add definitions
                if 'entries' in lexical_entry:
                    for entry in lexical_entry['entries']:
                        if 'senses' in entry:
                            for sense in entry['senses']:
                                if 'definitions' in sense:
                                    for definition in sense['definitions']:
                                        if lexical_category not in lexical_categories:
                                            lexical_category = 'other'

                                        VocabDefinition.objects.create(
                                            vocab_entry=vocab_entry,
                                            definition_type=lexical_categories[lexical_category],
                                            definition=definition
                                        )
