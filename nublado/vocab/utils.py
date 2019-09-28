import requests
from jsonschema import validate as validate_schema

from rest_framework import status

from django.contrib.auth import get_user_model

from .conf import settings
from .models import (
    VocabContextEntry, VocabEntry,
    VocabEntryJsonData, VocabSource
)
from .serializers import (
    VocabEntrySerializer,
    VocabContextSerializer,
    VocabSourceSerializer
)

User = get_user_model()


def export_vocab_entries(request=None, language=None):
    """
    Generates a serialized backup of vocab entries.
    """
    vocab_entries_dict = {}
    qs = VocabEntry.objects

    if language and language in settings.LANGUAGES_DICT:
        qs = qs.filter(language=language)

    vocab_entries_dict["vocab_entries"] = []

    for vocab_entry in qs.all():
        vocab_entry_dict = {}
        vocab_entry_serializer = VocabEntrySerializer(
            vocab_entry,
            context={"request": request},
        )
        vocab_entry_dict["vocab_entry_data"] = vocab_entry_serializer.get_minimal_data()
        vocab_entries_dict["vocab_entries"].append(vocab_entry_dict)

    return vocab_entries_dict


def export_vocab_source(request=None, vocab_source=None):
    """
    Generates a serialized backup of a vocab source.
    """
    if vocab_source:
        vocab_source_serializer = VocabSourceSerializer(
            vocab_source,
            context={"request": request}
        )
        vocab_source_dict = {
            "vocab_source_data": vocab_source_serializer.get_minimal_data()
        }

        if vocab_source.vocab_contexts.count():
            vocab_source_dict["vocab_contexts"] = []

            for vocab_context in vocab_source.vocab_contexts.all():
                vocab_context_serializer = VocabContextSerializer(
                    vocab_context,
                    context={"request": request}
                )
                vocab_context_dict = {
                    "vocab_context_data": vocab_context_serializer.get_minimal_data(),
                }

                if vocab_context.vocabcontextentry_set.count():
                    vocab_context_dict["vocab_entries"] = []
                    for vocab_context_entry in vocab_context.vocabcontextentry_set.all():
                        vocab_entry = vocab_context_entry.vocab_entry
                        vocab_entry_serializer = VocabEntrySerializer(
                            vocab_entry,
                            context={"request": request}
                        )
                        vocab_context_dict["vocab_entries"].append(
                            {
                                "vocab_entry_data": vocab_entry_serializer.get_minimal_data(),
                                "vocab_entry_tags": vocab_context_entry.get_vocab_entry_tags()
                            }
                        )

                vocab_source_dict["vocab_contexts"].append(vocab_context_dict)

        return vocab_source_dict


def import_vocab_entries(data):
    """
    Deserialzes data from vocab entries backup. (See export_vocab_entries)
    """
    validate_vocab_entries_json_schema(data)

    for vocab_entry_dict in data["vocab_entries"]:
        vocab_entry_data = vocab_entry_dict["vocab_entry_data"]

        if not VocabEntry.objects.filter(
            entry=vocab_entry_data["entry"],
            language=vocab_entry_data["language"]
        ).exists():
            VocabEntry.objects.create(
                **vocab_entry_data
            )


def import_vocab_source(data, user):
    """
    data: Serialized json data from vocab source backup.
    """
    validate_vocab_source_json_schema(data)

    user_id = user.id
    vocab_source_data = data["vocab_source_data"]

    VocabSource.objects.filter(
        creator_id=user_id,
        name=data["vocab_source_data"]["name"]
    ).delete()

    vocab_source_serializer = VocabSourceSerializer(
        data=vocab_source_data
    )
    vocab_source_serializer.is_valid(raise_exception=True)
    vocab_source = vocab_source_serializer.save(
        creator_id=user_id
    )

    if "vocab_contexts" in data:

        for vocab_context_dict in data["vocab_contexts"]:
            vocab_context_data = vocab_context_dict["vocab_context_data"]
            vocab_context_serializer = VocabContextSerializer(
                data=vocab_context_data
            )
            vocab_context_serializer.is_valid(raise_exception=True)
            vocab_context = vocab_context_serializer.save(
                vocab_source_id=vocab_source.id
            )

            if "vocab_entries" in vocab_context_dict:

                for vocab_context_entry_dict in vocab_context_dict["vocab_entries"]:
                    vocab_entry_data = vocab_context_entry_dict["vocab_entry_data"]

                    try:
                        vocab_entry = VocabEntry.objects.get(
                            entry=vocab_entry_data["entry"],
                            language=vocab_entry_data["language"]
                        )
                    except VocabEntry.DoesNotExist:
                        vocab_entry = VocabEntry.objects.create(
                            **vocab_entry_data
                        )

                    vocab_context_entry = VocabContextEntry.objects.create(
                        vocab_entry_id=vocab_entry.id,
                        vocab_context_id=vocab_context.id
                    )

                    if "vocab_entry_tags" in vocab_context_entry_dict:
                        for vocab_entry_tag in vocab_context_entry_dict["vocab_entry_tags"]:
                            vocab_context_entry.add_vocab_entry_tag(vocab_entry_tag)
                        vocab_context_entry.save()


def validate_vocab_entries_json_schema(data):
    schema = {
        "type": "object",
        "properties": {
            "vocab_entries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "vocab_entry_data": {
                            "type": "object",
                            "properties": {
                                "language": {
                                    "type": "string",
                                    "minLength": 2,
                                    "maxLength": 2,
                                },
                                "entry": {
                                    "type": "string"
                                },
                                "pronunciation_spelling": {
                                    "type": "string",
                                    "blank": True
                                },
                                "pronunciation_ipa": {
                                    "type": "string",
                                    "blank": True
                                },
                                "description": {
                                    "type": "string",
                                    "blank": True
                                },
                                "date_created": {
                                    "type": "string"
                                }
                            },
                            "required": ["entry"]
                        },
                    },
                    "required": ["vocab_entry_data"],
                },
            },
        },
        "required": ["vocab_entries"],
    }
    validate_schema(data, schema)


def validate_vocab_source_json_schema(data):
    schema = {
        "type": "object",
        "properties": {
            "vocab_source_data": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                    },
                    "description": {
                        "type": "string",
                        "blank": True,
                    },
                    "source_type": {
                        "type": "integer",
                    },
                    "date_created": {
                        "type": "string"
                    }
                },
                "required": ["name"],
            },
            "vocab_contexts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "vocab_context_data": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string"
                                },
                                "date_created": {
                                    "type": "string"
                                }
                            },
                            "required": ["content"],
                        },
                        "vocab_entries": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "vocab_entry_data": {
                                        "type": "object",
                                        "properties": {
                                            "language": {
                                                "type": "string",
                                                "minLength": 2,
                                                "maxLength": 2
                                            },
                                            "entry": {
                                                "type": "string",
                                            },
                                            "pronunciation_ipa": {
                                                "type": "string",
                                                "blank": True
                                            },
                                            "pronunciation_spelling": {
                                                "type": "string",
                                                "blank": True
                                            },
                                            "date_created": {
                                                "type": "string"
                                            }
                                        },
                                        "required": ["entry"],
                                    },
                                    "vocab_entry_tags": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "required": ["vocab_entry_data", "vocab_entry_tags"]
                            },
                        },
                    },
                    "required": ["vocab_context_data"]
                },
            },
        },
        "required": ["vocab_source_data"]
    }
    validate_schema(data, schema)


# Oxford API stuff
def get_oxford_entry_json(api_id, api_key, vocab_entry):
    """
    api_id: Oxford api id
    api_key: Oxford api key
    vocab_entry: A VocabEntry object
    """

    json_data = {}

    if VocabEntryJsonData.objects.filter(
        vocab_entry=vocab_entry,
        json_data_source=VocabEntryJsonData.OXFORD
    ).exists():
        json_data = VocabEntryJsonData.objects.get(
            vocab_entry=vocab_entry,
            json_data_source=VocabEntryJsonData.OXFORD
        ).json_data
    else:
        language = "en-us" if vocab_entry.language == "en" else vocab_entry.language
        oxford_entry_url = "{url}/entries/{language}/{entry}".format(
            url=settings.OXFORD_API_URL,
            language=language,
            entry=vocab_entry.entry
        )
        response = requests.get(
            oxford_entry_url,
            headers={
                "Accept": "application/json",
                "app_id": api_id,
                "app_key": api_key
            }
        )

        if response.status_code == status.HTTP_200_OK:
            json_data = response.json()
            VocabEntryJsonData.objects.create(
                vocab_entry=vocab_entry,
                json_data=json_data,
                json_data_source=VocabEntryJsonData.OXFORD
            )

    return json_data


def parse_oxford_entry_json(json_data):
    results_dict = {
        "lexicalEntries": []
    }

    for result in json_data["results"]:
        if "lexicalEntries" in result:
            for lexical_entry in result["lexicalEntries"]:
                lexical_entry_dict = {
                    "lexicalCategory": lexical_entry["lexicalCategory"]["text"].lower(),
                    "pronunciations": {
                        "ipa": [],
                        "audioFile": ""
                    },
                    "definitions": []
                }

                if "pronunciations" in lexical_entry:
                    for pronunciation in lexical_entry["pronunciations"]:
                        if "phoneticNotation" in pronunciation:
                            if pronunciation["phoneticNotation"].lower() == "ipa":
                                pronunciation_dict = {
                                    "phoneticSpelling": "",
                                    "audioFile": ""
                                }

                                if "phoneticSpelling" in pronunciation:
                                    pronunciation_dict["phoneticSpelling"] = pronunciation["phoneticSpelling"]

                                if "audioFile" in pronunciation:
                                    pronunciation_dict["audioFile"] = pronunciation["audioFile"]

                                lexical_entry_dict["pronunciations"]["ipa"].append(pronunciation_dict)

                if "entries" in lexical_entry:
                    for entry in lexical_entry["entries"]:
                        if "senses" in entry:
                            for sense in entry["senses"]:
                                if "definitions" in sense:
                                    for definition in sense["definitions"]:
                                        lexical_entry_dict["definitions"].append(definition)

                results_dict["lexicalEntries"].append(lexical_entry_dict)

    return results_dict
