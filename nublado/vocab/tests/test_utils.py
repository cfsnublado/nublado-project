import json

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase

from ..models import (
    VocabContext, VocabContextEntry, VocabEntry,
    VocabProject, VocabSource
)
from ..serializers import (
    VocabContextSerializer, VocabEntrySerializer,
    VocabProjectSerializer, VocabSourceSerializer
)
from ..utils import (
    export_vocab_entries, export_vocab_source,
    import_vocab_entries, import_vocab_source,
    validate_vocab_source_json_schema
)

User = get_user_model()


class TestCommon(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_superuser(
            username='cfs',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@foo.com',
            password=self.pwd
        )


class ExportVocabEntriesTest(TestCommon):

    def setUp(self):
        super(ExportVocabEntriesTest, self).setUp()
        self.request = self.request_factory.get('/fake-path')
        self.request.user = self.user
        self.user_2 = User.objects.create_user(
            username='kfl7',
            first_name='Karen',
            last_name='Fuentes',
            email='kfl7@foo.com',
            password=self.pwd
        )

    def test_export_entries_data(self):
        vocab_entries = [
            VocabEntry.objects.create(entry='foo en 1', language='en'),
            VocabEntry.objects.create(entry='foo en 3', language='en'),
            VocabEntry.objects.create(entry='foo es 2', language='es'),
            VocabEntry.objects.create(entry='foo es 3', language='es')
        ]
        expected_data = {'vocab_entries': []}
        for vocab_entry in vocab_entries:
            serializer = VocabEntrySerializer(
                vocab_entry,
                context={'request': self.request}
            )
            expected_data['vocab_entries'].append(
                {'vocab_entry_data': serializer.get_minimal_data()}
            )
        data = export_vocab_entries(self.request)
        self.assertEqual(expected_data, data)

    def test_export_entries_all(self):
        vocab_entries = []
        vocab_entries.append(VocabEntry.objects.create(entry='foo en 1', language='en'))
        vocab_entries.append(VocabEntry.objects.create(entry='foo en 3', language='en'))
        vocab_entries.append(VocabEntry.objects.create(entry='foo es 1', language='es'))
        vocab_entries.append(VocabEntry.objects.create(entry='foo es 3', language='es'))

        data = export_vocab_entries(self.request)
        self.assertEqual(
            len(data['vocab_entries']), len(vocab_entries)
        )

    def test_export_entries_by_language(self):
        VocabEntry.objects.create(entry='foo en 1', language='en')
        VocabEntry.objects.create(entry='foo en 2', language='en')
        VocabEntry.objects.create(entry='foo en 3', language='en')
        VocabEntry.objects.create(entry='foo es 2', language='es')
        VocabEntry.objects.create(entry='foo es 3', language='es')

        data = export_vocab_entries(self.request, language='es')

        for vocab_entry in data['vocab_entries']:
            self.assertEqual(vocab_entry['vocab_entry_data']['language'], 'es')

        data = export_vocab_entries(self.request, language='en')

        for vocab_entry in data['vocab_entries']:
            self.assertEqual(vocab_entry['vocab_entry_data']['language'], 'en')


class ImportVocabEntriesTest(TestCommon):

    def setUp(self):
        super(ImportVocabEntriesTest, self).setUp()
        self.request = self.request_factory.get('/fake-path')
        self.request.user = self.user

    def test_import_vocab_entries_from_export_vocab_entries(self):
        vocab_entries = [
            VocabEntry.objects.create(entry='foo en 1', language='en'),
            VocabEntry.objects.create(entry='foo en 2', language='en'),
            VocabEntry.objects.create(entry='foo es 1', language='es'),
            VocabEntry.objects.create(entry='foo es 2', language='es'),
        ]
        data = export_vocab_entries(self.request)
        VocabEntry.objects.all().delete()
        self.assertEqual(VocabEntry.objects.count(), 0)
        import_vocab_entries(data)
        self.assertEqual(VocabEntry.objects.count(), len(vocab_entries))


class ExportVocabSourceTest(TestCommon):

    def setUp(self):
        super(ExportVocabSourceTest, self).setUp()
        self.request = self.request_factory.get('/fake-path')
        self.request.user = self.user
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )

    def test_export_vocab_source_data(self):
        vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='Test source',
            source_type=VocabSource.BOOK
        )
        vocab_context = VocabContext.objects.create(
            vocab_source=vocab_source,
            content='This is a sample sentence.'
        )
        vocab_entry = VocabEntry.objects.create(
            entry='sentence',
            language='en'
        )
        vocab_context_entry = VocabContextEntry.objects.create(
            vocab_context=vocab_context,
            vocab_entry=vocab_entry
        )
        vocab_project_serializer = VocabProjectSerializer(
            self.vocab_project,
            context={'request': self.request}
        )
        vocab_source_serializer = VocabSourceSerializer(
            vocab_source,
            context={'request': self.request}
        )
        vocab_context_serializer = VocabContextSerializer(
            vocab_context,
            context={'request': self.request}
        )
        vocab_entry_serializer = VocabEntrySerializer(
            vocab_entry,
            context={'request': self.request}
        )
        expected_data = json.loads(json.dumps({
            'vocab_project_data': vocab_project_serializer.get_minimal_data(),
            'vocab_source_data': vocab_source_serializer.get_minimal_data(),
            'vocab_contexts': [
                {
                    'vocab_context_data': vocab_context_serializer.get_minimal_data(),
                    'vocab_entries': [
                        {
                            'vocab_entry_data': vocab_entry_serializer.get_minimal_data(),
                            'vocab_entry_tags': vocab_context_entry.get_vocab_entry_tags(),
                        }
                    ]
                }
            ]
        }))
        data = export_vocab_source(self.request, vocab_source)
        self.assertEqual(expected_data, data)


class ImportVocabSourceTest(TestCommon):

    def setUp(self):
        super(ImportVocabSourceTest, self).setUp()
        self.request = self.request_factory.get('/fake-path')
        self.request.user = self.user
        self.vocab_project = VocabProject.objects.create(
            name='test project',
            owner=self.user
        )

    def test_import_vocab_source_data(self):
        vocab_source = VocabSource.objects.create(
            creator=self.user,
            vocab_project=self.vocab_project,
            name='Test source',
            source_type=VocabSource.BOOK
        )
        vocab_context = VocabContext.objects.create(
            vocab_source=vocab_source,
            content='This is a sample sentence.'
        )
        vocab_entry = VocabEntry.objects.create(
            entry='sentence',
            language='en'
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
            vocab_project=self.vocab_project,
            name='Test source',
            source_type=VocabSource.BOOK
        )
        vocab_context = VocabContext.objects.get(
            vocab_source=vocab_source,
            content='This is a sample sentence.'
        )
        vocab_entry = VocabEntry.objects.get(
            entry='sentence',
            language='en'
        )
        self.assertTrue(
            VocabContextEntry.objects.filter(
                vocab_context=vocab_context,
                vocab_entry=vocab_entry
            ).exists()
        )


class ValidateVocabSourceJSONTest(TestCommon):

    def setUp(self):
        super(ValidateVocabSourceJSONTest, self).setUp()
        self.request = self.request_factory.get('/fake-path')
        self.request.user = self.user
        self.vocab_project = VocabProject.objects.create(
            name='test project',
            owner=self.user
        )

    def test_validate_vocab_source_data(self):
        vocab_source = VocabSource.objects.create(
            creator=self.user,
            vocab_project=self.vocab_project,
            name='Test source',
            source_type=VocabSource.BOOK
        )
        vocab_context = VocabContext.objects.create(
            vocab_source=vocab_source,
            content='This is a sample sentence.'
        )
        vocab_entry = VocabEntry.objects.create(
            entry='sentence',
            language='en'
        )
        vocab_context_entry = VocabContextEntry.objects.create(
            vocab_context=vocab_context,
            vocab_entry=vocab_entry
        )
        vocab_project_serializer = VocabProjectSerializer(
            self.vocab_project,
            context={'request': self.request}
        )
        vocab_source_serializer = VocabSourceSerializer(
            vocab_source,
            context={'request': self.request}
        )
        vocab_context_serializer = VocabContextSerializer(
            vocab_context,
            context={'request': self.request}
        )
        vocab_entry_serializer = VocabEntrySerializer(
            vocab_entry,
            context={'request': self.request}
        )
        data = {
            'vocab_project_data': vocab_project_serializer.get_minimal_data(),
            'vocab_source_data': vocab_source_serializer.get_minimal_data(),
            'vocab_contexts': [
                {
                    'vocab_context_data': vocab_context_serializer.get_minimal_data(),
                    'vocab_entries': [
                        {
                            'vocab_entry_data': vocab_entry_serializer.get_minimal_data(),
                            'vocab_entry_tags': vocab_context_entry.get_vocab_entry_tags(),
                        }
                    ]
                }
            ]
        }
        validate_vocab_source_json_schema(json.loads(json.dumps(data)))
