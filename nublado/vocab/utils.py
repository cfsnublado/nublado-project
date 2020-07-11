import random
import re
import requests
from jsonschema import validate as validate_schema
import markdown2
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from rest_framework import status

from django.contrib.auth import get_user_model

from .conf import settings
from .models import (
    VocabContextAudio, VocabContextEntry, VocabEntry,
    VocabEntryJsonData, VocabSource
)
from .serializers import (
    VocabEntrySerializer,
    VocabContextSerializer,
    VocabSourceSerializer
)

User = get_user_model()


def get_random_vocab_entry(language=None):
    vocab_entry = None

    if language is None:
        queryset = VocabEntry.objects.all()
    else:
        queryset = VocabEntry.objects.filter(language=language)

    if len(queryset):
        vocab_entry = random.choice(queryset)

    return vocab_entry


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

            for vocab_context in vocab_source.vocab_contexts.all().order_by("date_created"):
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


def vocab_source_markdown_to_dict(md_text):
    html = markdown2.markdown(
        md_text,
        extras=["metadata", "markdown-in-html"]
    )
    source_data = {}

    if "source_name" not in html.metadata:
        raise TypeError("Missing source_name attribute in metadata.")

    source_data["name"] = html.metadata["source_name"]

    if "source_type" in html.metadata:
        vocab_source_type = getattr(
            VocabSource, html.metadata["source_type"].upper(),
            None
        )

        if vocab_source_type is not None:
            source_data["source_type"] = vocab_source_type

    if "source_description" in html.metadata:
        source_data["description"] = html.metadata["source_description"]

    data_dict = {
        "vocab_source_data": source_data,
        "vocab_contexts": []
    }
    soup = BeautifulSoup(html, "html.parser")
    lis = soup.ul.find_all("li", recursive=False)

    for li in lis:
        vocab_context_dict = {
            "vocab_context_data": {}
        }
        # Tagged entries
        tagged_vocab = li.find("div", "tagged-entries")

        if tagged_vocab:
            vocab_context_dict["vocab_entries"] = []

            for entry_tag in tagged_vocab.find_all("p", recursive=False):
                # entry: language: tag1, tag2, tag3...
                entry_list = [x.strip() for x in entry_tag.string.split(":")]
                tags = [x.strip() for x in entry_list[2].split(",")]
                vocab_context_dict["vocab_entries"].append(
                    {
                        "vocab_entry_data": {
                            "language": entry_list[0],
                            "entry": entry_list[1]
                        },
                        "vocab_entry_tags": tags
                    }
                )

            tagged_vocab.extract()

        # VocabContextAudio
        vocab_context_audios = li.find("div", "vocab-context-audios")

        if vocab_context_audios:
            vocab_context_dict["vocab_context_audios"] = []

            for vocab_context_audio in vocab_context_audios.find_all("p", recursive=False):
                # audio title: audio file link
                audio_list = [x.strip() for x in re.split(r':(?!//)', vocab_context_audio.string)]
                vocab_context_dict["vocab_context_audios"].append(
                    {
                        "vocab_context_audio_data": {
                            "name": audio_list[0],
                            "audio_url": audio_list[1]
                        }
                    }
                )

            vocab_context_audios.extract()

        li_content = li.decode_contents()

        # Revert li content back to markdown. (Hacky I know).
        vocab_context_dict["vocab_context_data"]["content"] = md(li_content)
        data_dict["vocab_contexts"].append(vocab_context_dict)

    print("{0} markdown has been converted.".format(source_data["name"]))

    return data_dict


def import_vocab_source_json(data, user):
    """
    data: Serialized vocab source json data
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
        vocab_context_order = 1

        for vocab_context_dict in data["vocab_contexts"]:
            vocab_context_data = vocab_context_dict["vocab_context_data"]
            vocab_context_serializer = VocabContextSerializer(
                data=vocab_context_data
            )
            vocab_context_serializer.is_valid(raise_exception=True)
            vocab_context = vocab_context_serializer.save(
                vocab_source_id=vocab_source.id,
                order=vocab_context_order
            )
            vocab_context_order += 1

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

            if "vocab_context_audios" in vocab_context_dict:
                for vocab_context_audio_dict in vocab_context_dict["vocab_context_audios"]:
                    vocab_context_audio_data = vocab_context_audio_dict["vocab_context_audio_data"]
                    VocabContextAudio.objects.create(
                        creator_id=user_id,
                        vocab_context_id=vocab_context.id,
                        name=vocab_context_audio_data["name"],
                        audio_url=vocab_context_audio_data["audio_url"]
                    )


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
                            "vocab_context_audios": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "vocab_context_audio_data": {
                                            "type": "object",
                                            "properties": {
                                                "name": {
                                                    "type": "string",
                                                },
                                                "audio_url": {
                                                    "type": "string"
                                                },
                                            },
                                        }
                                    },
                                    "required": ["vocab_context_audio_data"]
                                }
                            }
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


def parse_oxford_entry_json(json_data, language="en"):
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
                    "definitions": [],
                }

                if "entries" in lexical_entry:
                    for entry in lexical_entry["entries"]:
                        if "pronunciations" in entry:
                            for pronunciation in entry["pronunciations"]:
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

                        if "senses" in entry:
                            for sense in entry["senses"]:
                                if "definitions" in sense:
                                    for definition in sense["definitions"]:
                                        lexical_entry_dict["definitions"].append(definition)

                                if "subsenses" in sense:
                                    for subsense in sense["subsenses"]:
                                        if "definitions" in subsense:
                                            for definition in subsense["definitions"]:
                                                lexical_entry_dict["definitions"].append(definition)

                results_dict["lexicalEntries"].append(lexical_entry_dict)

    return results_dict
