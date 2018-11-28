import json
from jsonschema import validate as validate_schema

from django.contrib.auth import get_user_model

from .conf import settings
from .models import (
    VocabEntry, VocabContextEntry,
    VocabProject, VocabSource
)
from .serializers import (
    VocabEntrySerializer, VocabContextSerializer,
    VocabProjectSerializer, VocabSourceSerializer
)

User = get_user_model()


def export_vocab_entries(request, language=None):
    '''
    Generates a serialized backup of vocab entries.
    '''
    vocab_data = {}
    qs = VocabEntry.objects
    if language and language in settings.LANGUAGES_DICT:
        qs = qs.filter(language=language)
    vocab_data.update({'vocab_entries': {}})
    for vocab_entry_index, vocab_entry in enumerate(qs.all(), start=1):
        vocab_entry_serializer = VocabEntrySerializer(
            vocab_entry,
            context={'request': request},
        )
        vocab_data['vocab_entries'][vocab_entry_index] = {
            'vocab_entry_data': vocab_entry_serializer.get_minimal_data()
        }
    return json.loads(json.dumps(vocab_data))


def export_vocab_source(request, vocab_source):
    '''
    Generates a serialized backup of a vocab source.
    '''
    if request and vocab_source:
        vocab_project_serializer = VocabProjectSerializer(
            vocab_source.vocab_project,
            context={'request': request}
        )
        vocab_source_serializer = VocabSourceSerializer(
            vocab_source,
            context={'request': request}
        )
        vocab_data = {
            'vocab_project_data': vocab_project_serializer.get_minimal_data(),
            'vocab_source_data': vocab_source_serializer.get_minimal_data(),
            'vocab_contexts': {},
        }
        for vocab_context_index, vocab_context in enumerate(vocab_source.vocab_contexts.all(), start=1):
            vocab_context_serializer = VocabContextSerializer(
                vocab_context,
                context={'request': request}
            )
            vocab_context_dict = {
                'vocab_context_data': vocab_context_serializer.get_minimal_data(),
                'vocab_entries': []
            }
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
            vocab_data['vocab_contexts'][vocab_context_index] = vocab_context_dict
        return json.loads(json.dumps(vocab_data))


def import_vocab_entries(data):
    '''
    Deserialzes data from vocab entries backup. (See export_vocab_entries)
    '''
    validate_vocab_entries_json_schema(data)
    for vocab_entry_k, vocab_entry_v in data['vocab_entries'].items():
        vocab_entry_data = vocab_entry_v['vocab_entry_data']
        if not VocabEntry.objects.filter(
            entry=vocab_entry_data['entry'],
            language=vocab_entry_data['language']
        ).exists():
            VocabEntry.objects.create(
                **vocab_entry_data
            )


def import_vocab_source(data, creator):
    '''
    data: Serialized json data from vocab source backup.
    '''
    validate_vocab_source_json_schema(data)
    creator_id = creator.id
    vocab_contexts_dict = data['vocab_contexts']
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
    for vocab_context_k, vocab_context_v in vocab_contexts_dict.items():
        vocab_context_data = vocab_context_v['vocab_context_data']
        vocab_context_serializer = VocabContextSerializer(
            data=vocab_context_data
        )
        vocab_context_serializer.is_valid(raise_exception=True)
        vocab_context = vocab_context_serializer.save(
            vocab_source_id=vocab_source.id
        )
        # VocabContextEntry
        for vocab_context_entry in vocab_context_v['vocab_entries']:
            vocab_entry_data = vocab_context_entry['vocab_entry_data']
            try:
                vocab_entry = VocabEntry.objects.get(
                    entry=vocab_entry_data['entry'],
                    language=vocab_entry_data['language']
                )
            except VocabEntry.DoesNotExist:
                vocab_entry = VocabEntry.objects.create(
                    **vocab_entry_data
                )
            vocab_context_entry_obj = VocabContextEntry.objects.create(
                vocab_entry_id=vocab_entry.id,
                vocab_context_id=vocab_context.id
            )
            if vocab_context_entry['vocab_entry_tags']:
                for vocab_entry_tag in vocab_context_entry['vocab_entry_tags']:
                    vocab_context_entry_obj.add_vocab_entry_tag(vocab_entry_tag)
                vocab_context_entry_obj.save()


def validate_vocab_entries_json_schema(data):
    schema = {
        'type': 'object',
        'properties': {
            'vocab_entries': {
                'type': 'object',
                'patternProperties': {
                    '^[0-9]+$': {
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
                    }
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
                'type': 'object',
                'patternProperties': {
                    '^[0-9]+$': {
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
                                }
                            }
                        },
                        'required': ['vocab_context_data', 'vocab_entries']
                    },
                }
            }
        },
        'required': ['vocab_source_data', 'vocab_contexts']
    }
    validate_schema(data, schema)
