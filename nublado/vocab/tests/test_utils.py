import json

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase

from ..models import VocabContext, VocabContextEntry, VocabEntry, VocabSource
from ..serializers import VocabContextSerializer, VocabEntrySerializer, VocabSourceSerializer
from ..utils import (
    export_vocab_entries, export_vocab_source,
    import_vocab_entries, import_vocab_source,
    validate_vocab_source_json_schema
)

User = get_user_model()


class TestCommon(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.pwd = "Pizza?69p"
        self.user = User.objects.create_superuser(
            username="cfs",
            first_name="Christopher",
            last_name="Sanders",
            email="cfs7@foo.com",
            password=self.pwd
        )


class ExportVocabEntriesTest(TestCommon):

    def setUp(self):
        super(ExportVocabEntriesTest, self).setUp()
        self.request = self.request_factory.get("/fake-path")
        self.request.user = self.user
        self.user_2 = User.objects.create_user(
            username="kfl7",
            first_name="Karen",
            last_name="Fuentes",
            email="kfl7@foo.com",
            password=self.pwd
        )

    def test_export_entries_data(self):
        vocab_entries = [
            VocabEntry.objects.create(creator=self.user, entry="foo en 1", language="en"),
            VocabEntry.objects.create(creator=self.user_2, entry="foo en 3", language="en"),
            VocabEntry.objects.create(creator=self.user, entry="foo es 2", language="es"),
            VocabEntry.objects.create(creator=self.user_2, entry="foo es 3", language="es")
        ]
        expected_data = {"vocab_entries": {}}
        for vocab_entry in vocab_entries:
            serializer = VocabEntrySerializer(
                vocab_entry,
                context={"request": self.request}
            )
            expected_data["vocab_entries"].update(
                {str(vocab_entry.id): {"vocab_entry_data": serializer.get_minimal_data()}}
            )
        data = export_vocab_entries(self.request)
        self.assertEqual(expected_data, data)

    def test_export_entries_no_creator_no_language(self):
        vocab_entry_dict = {}
        vocab_entry = VocabEntry.objects.create(creator=self.user, entry="foo en 1", language="en")
        vocab_entry_dict[str(vocab_entry.id)] = vocab_entry
        vocab_entry = VocabEntry.objects.create(creator=self.user_2, entry="foo en 3", language="en")
        vocab_entry_dict[str(vocab_entry.id)] = vocab_entry
        vocab_entry = VocabEntry.objects.create(creator=self.user, entry="foo es 1", language="es")
        vocab_entry_dict[str(vocab_entry.id)] = vocab_entry
        vocab_entry = VocabEntry.objects.create(creator=self.user_2, entry="foo es 3", language="es")
        vocab_entry_dict[str(vocab_entry.id)] = vocab_entry

        data = export_vocab_entries(self.request)
        self.assertEqual(
            len(data["vocab_entries"].keys()), len(vocab_entry_dict.keys())
        )
        for k, v in data["vocab_entries"].items():
            self.assertTrue(k in vocab_entry_dict)
            vocab_entry = vocab_entry_dict[k]
            serializer = VocabEntrySerializer(vocab_entry, context={"request": self.request})
            self.assertEqual(v, {"vocab_entry_data": serializer.get_minimal_data()})

    def test_export_entries_creator(self):
        vocab_entry_dict = {}
        vocab_entry = VocabEntry.objects.create(creator=self.user, entry="foo en 1", language="en")
        vocab_entry_dict[str(vocab_entry.id)] = vocab_entry
        vocab_entry = VocabEntry.objects.create(creator=self.user, entry="foo en 2", language="en")
        vocab_entry_dict[str(vocab_entry.id)] = vocab_entry
        vocab_entry = VocabEntry.objects.create(creator=self.user, entry="foo es 1", language="es")
        vocab_entry_dict[str(vocab_entry.id)] = vocab_entry
        vocab_entry = VocabEntry.objects.create(creator=self.user, entry="foo es 2", language="es")
        vocab_entry_dict[str(vocab_entry.id)] = vocab_entry

        VocabEntry.objects.create(creator=self.user_2, entry="foo en 3", language="en"),
        VocabEntry.objects.create(creator=self.user_2, entry="foo es 3", language="es")

        data = export_vocab_entries(self.request, creator=self.user)
        self.assertEqual(
            len(data["vocab_entries"].keys()), len(vocab_entry_dict.keys())
        )
        for k, v in data["vocab_entries"].items():
            self.assertTrue(k in vocab_entry_dict)
            vocab_entry = vocab_entry_dict[k]
            serializer = VocabEntrySerializer(vocab_entry, context={"request": self.request})
            self.assertEqual(v, {"vocab_entry_data": serializer.get_minimal_data()})

    def test_export_entries_language(self):
        vocab_entry_en_dict = {}
        vocab_entry = VocabEntry.objects.create(creator=self.user, entry="foo en 1", language="en")
        vocab_entry_en_dict[str(vocab_entry.id)] = vocab_entry
        vocab_entry = VocabEntry.objects.create(creator=self.user, entry="foo en 2", language="en")
        vocab_entry_en_dict[str(vocab_entry.id)] = vocab_entry
        vocab_entry = VocabEntry.objects.create(creator=self.user_2, entry="foo en 3", language="en")
        vocab_entry_en_dict[str(vocab_entry.id)] = vocab_entry

        vocab_entry_es_dict = {}
        vocab_entry = VocabEntry.objects.create(creator=self.user, entry="foo es 2", language="es")
        vocab_entry_es_dict[str(vocab_entry.id)] = vocab_entry
        vocab_entry = VocabEntry.objects.create(creator=self.user_2, entry="foo es 3", language="es")
        vocab_entry_es_dict[str(vocab_entry.id)] = vocab_entry

        data = export_vocab_entries(self.request, language="es")
        self.assertEqual(
            len(data["vocab_entries"].keys()), len(vocab_entry_es_dict.keys())
        )
        for k, v in data["vocab_entries"].items():
            self.assertTrue(k in vocab_entry_es_dict)
            vocab_entry = vocab_entry_es_dict[k]
            serializer = VocabEntrySerializer(vocab_entry, context={"request": self.request})
            self.assertEqual(v, {"vocab_entry_data": serializer.get_minimal_data()})

        data = export_vocab_entries(self.request, language="en")
        self.assertEqual(
            len(data["vocab_entries"].keys()), len(vocab_entry_en_dict.keys())
        )
        for k, v in data["vocab_entries"].items():
            self.assertTrue(k in vocab_entry_en_dict)
            vocab_entry = vocab_entry_en_dict[k]
            serializer = VocabEntrySerializer(vocab_entry, context={"request": self.request})
            self.assertEqual(v, {"vocab_entry_data": serializer.get_minimal_data()})

    def test_export_entries_creator_language(self):
        vocab_entry_en_user_1_dict = {}
        vocab_entry = VocabEntry.objects.create(creator=self.user, entry="foo en 1", language="en")
        vocab_entry_en_user_1_dict[str(vocab_entry.id)] = vocab_entry
        vocab_entry = VocabEntry.objects.create(creator=self.user, entry="foo en 2", language="en")
        vocab_entry_en_user_1_dict[str(vocab_entry.id)] = vocab_entry

        vocab_entry_es_user_1_dict = {}
        vocab_entry = VocabEntry.objects.create(creator=self.user, entry="foo es 1", language="es")
        vocab_entry_es_user_1_dict[str(vocab_entry.id)] = vocab_entry
        vocab_entry = VocabEntry.objects.create(creator=self.user, entry="foo es 2", language="es")
        vocab_entry_es_user_1_dict[str(vocab_entry.id)] = vocab_entry

        vocab_entry_en_user_2_dict = {}
        vocab_entry = VocabEntry.objects.create(creator=self.user_2, entry="foo en 3", language="en")
        vocab_entry_en_user_2_dict[str(vocab_entry.id)] = vocab_entry

        vocab_entry_es_user_2_dict = {}
        vocab_entry = VocabEntry.objects.create(creator=self.user_2, entry="foo es 3", language="es")
        vocab_entry_es_user_2_dict[str(vocab_entry.id)] = vocab_entry

        data = export_vocab_entries(self.request, creator=self.user, language="es")
        self.assertEqual(
            len(data["vocab_entries"].keys()), len(vocab_entry_es_user_1_dict.keys())
        )
        for k, v in data["vocab_entries"].items():
            self.assertTrue(k in vocab_entry_es_user_1_dict)
            vocab_entry = vocab_entry_es_user_1_dict[k]
            serializer = VocabEntrySerializer(vocab_entry, context={"request": self.request})
            self.assertEqual(v, {"vocab_entry_data": serializer.get_minimal_data()})

        data = export_vocab_entries(self.request, creator=self.user_2, language="en")
        self.assertEqual(
            len(data["vocab_entries"].keys()), len(vocab_entry_en_user_2_dict.keys())
        )
        for k, v in data["vocab_entries"].items():
            self.assertTrue(k in vocab_entry_en_user_2_dict)
            vocab_entry = vocab_entry_en_user_2_dict[k]
            serializer = VocabEntrySerializer(vocab_entry, context={"request": self.request})
            self.assertEqual(v, {"vocab_entry_data": serializer.get_minimal_data()})


class ImportVocabEntriesTest(TestCommon):

    def setUp(self):
        super(ImportVocabEntriesTest, self).setUp()
        self.request = self.request_factory.get("/fake-path")
        self.request.user = self.user

    def test_import_vocab_entries_from_export_vocab_entries(self):
        vocab_entries = [
            VocabEntry.objects.create(creator=self.user, entry="foo en 1", language="en"),
            VocabEntry.objects.create(creator=self.user, entry="foo en 2", language="en"),
            VocabEntry.objects.create(creator=self.user, entry="foo es 1", language="es"),
            VocabEntry.objects.create(creator=self.user, entry="foo es 2", language="es"),
        ]
        data = export_vocab_entries(self.request)
        VocabEntry.objects.all().delete()
        self.assertEqual(VocabEntry.objects.count(), 0)
        import_vocab_entries(data, self.user)
        self.assertEqual(VocabEntry.objects.count(), len(vocab_entries))


class ExportVocabSourceTest(TestCommon):

    def setUp(self):
        super(ExportVocabSourceTest, self).setUp()
        self.request = self.request_factory.get("/fake-path")
        self.request.user = self.user

    def test_export_vocab_source_data(self):
        vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="Test source",
            source_type=VocabSource.BOOK
        )
        vocab_context = VocabContext.objects.create(
            vocab_source=vocab_source,
            content="This is a sample sentence."
        )
        vocab_entry = VocabEntry.objects.create(
            creator=self.user,
            entry="sentence",
            language="en"
        )
        vocab_context_entry = VocabContextEntry.objects.create(
            vocab_context=vocab_context,
            vocab_entry=vocab_entry
        )
        vocab_source_serializer = VocabSourceSerializer(
            vocab_source,
            context={"request": self.request}
        )
        vocab_context_serializer = VocabContextSerializer(
            vocab_context,
            context={"request": self.request}
        )
        vocab_entry_serializer = VocabEntrySerializer(
            vocab_entry,
            context={"request": self.request}
        )
        expected_data = json.loads(json.dumps({
            "creator_id": str(self.user.id),
            "vocab_source_data": vocab_source_serializer.get_minimal_data(),
            "vocab_contexts": {
                vocab_context.id: {
                    "vocab_context_data": vocab_context_serializer.get_minimal_data(),
                    "vocab_entries": [
                        {
                            "vocab_entry_data": vocab_entry_serializer.get_minimal_data(),
                            "vocab_entry_tags": vocab_context_entry.get_vocab_entry_tags(),
                        }
                    ]
                }
            }
        }))
        data = export_vocab_source(self.request, vocab_source)
        self.assertEqual(expected_data, data)


class ImportVocabSourceTest(TestCommon):

    def setUp(self):
        super(ImportVocabSourceTest, self).setUp()
        self.request = self.request_factory.get("/fake-path")
        self.request.user = self.user

    def test_import_vocab_source_data(self):
        vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="Test source",
            source_type=VocabSource.BOOK
        )
        vocab_context = VocabContext.objects.create(
            vocab_source=vocab_source,
            content="This is a sample sentence."
        )
        vocab_entry = VocabEntry.objects.create(
            creator=self.user,
            entry="sentence",
            language="en"
        )
        VocabContextEntry.objects.create(
            vocab_context=vocab_context,
            vocab_entry=vocab_entry
        )

        data = export_vocab_source(self.request, vocab_source)
        VocabSource.objects.all().delete()
        vocab_entry.delete()
        self.assertEqual(len(VocabSource.objects.all()), 0)
        self.assertEqual(len(VocabEntry.objects.all()), 0)
        self.assertEqual(len(VocabContext.objects.all()), 0)
        self.assertEqual(len(VocabEntry.objects.all()), 0)
        import_vocab_source(data, self.user)
        self.assertEqual(len(VocabSource.objects.all()), 1)
        vocab_source = VocabSource.objects.get(
            creator=self.user,
            name="Test source",
            source_type=VocabSource.BOOK
        )
        vocab_context = VocabContext.objects.get(
            vocab_source=vocab_source,
            content="This is a sample sentence."
        )
        vocab_entry = VocabEntry.objects.get(
            creator=self.user,
            entry="sentence",
            language="en"
        )
        self.assertTrue(
            VocabContextEntry.objects.filter(
                vocab_context=vocab_context,
                vocab_entry=vocab_entry
            ).exists()
        )

    def test_import_vocab_source_permissions(self):

        creator = User.objects.create_user(
            username="kfl7",
            email="kfl7@foo.com",
            first_name="Karen",
            last_name="Fuentes",
            password=self.pwd
        )
        non_creator = User.objects.create_user(
            username="foo7",
            email="foo7@foo.com",
            first_name="Foo",
            last_name="Foo",
            password=self.pwd
        )
        vocab_source = VocabSource.objects.create(
            creator=creator,
            name="Test source",
            source_type=VocabSource.BOOK
        )
        data = export_vocab_source(self.request, vocab_source)
        vocab_source.delete()

        # Superuser
        self.assertTrue(self.user.is_superuser)
        import_vocab_source(data, self.user)
        VocabSource.objects.get(creator=creator, name="Test source").delete()

        # Source creator
        import_vocab_source(data, creator)
        VocabSource.objects.get(creator=creator, name="Test source").delete()

        # Not source creator and not superuser
        with self.assertRaises(PermissionDenied):
            import_vocab_source(data, non_creator)


class ValidateVocabSourceJSONTest(TestCommon):

    def setUp(self):
        super(ValidateVocabSourceJSONTest, self).setUp()
        self.request = self.request_factory.get("/fake-path")
        self.request.user = self.user

    def test_validate_vocab_source_data(self):
        vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="Test source",
            source_type=VocabSource.BOOK
        )
        vocab_context = VocabContext.objects.create(
            vocab_source=vocab_source,
            content="This is a sample sentence."
        )
        vocab_entry = VocabEntry.objects.create(
            creator=self.user,
            entry="sentence",
            language="en"
        )
        vocab_context_entry = VocabContextEntry.objects.create(
            vocab_context=vocab_context,
            vocab_entry=vocab_entry
        )
        vocab_source_serializer = VocabSourceSerializer(
            vocab_source,
            context={"request": self.request}
        )
        vocab_context_serializer = VocabContextSerializer(
            vocab_context,
            context={"request": self.request}
        )
        vocab_entry_serializer = VocabEntrySerializer(
            vocab_entry,
            context={"request": self.request}
        )
        data = {
            "creator_id": str(self.user.id),
            "vocab_source_data": vocab_source_serializer.get_minimal_data(),
            "vocab_contexts": {
                vocab_context.id: {
                    "vocab_context_data": vocab_context_serializer.get_minimal_data(),
                    "vocab_entries": [
                        {
                            "vocab_entry_data": vocab_entry_serializer.get_minimal_data(),
                            "vocab_entry_tags": vocab_context_entry.get_vocab_entry_tags(),
                        }
                    ]
                }
            }
        }
        validate_vocab_source_json_schema(json.loads(json.dumps(data)))
