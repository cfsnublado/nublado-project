from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import (
    VocabContext, VocabContextEntry, VocabEntry,
    VocabSource
)

User = get_user_model()


class TestUserManager(TestCase):

    def setUp(self):
        self.vocab_context_entry_manager = VocabContextEntry.objects
        self.pwd = 'Coffee?69c'
        self.user = User.objects.create_user(
            username='cfs7',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@foo.com',
            password=self.pwd
        )
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name='Test Source'
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='Testing testing probando'
        )
        self.vocab_context_2 = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='Testing testing probando'
        )

    def test_source_entry_language_max(self):
        # Missing vocab source id.
        with self.assertRaises(TypeError):
            self.vocab_context_entry_manager.source_entry_language_max()

        # No entries in source.
        language = self.vocab_context_entry_manager.source_entry_language_max(self.vocab_source.id)
        self.assertIsNone(language)

        # More entries in en
        vocab_entry_en_1 = VocabEntry.objects.create(entry='test', language='en')
        vocab_entry_en_2 = VocabEntry.objects.create(entry='testing', language='en')
        vocab_entry_es_1 = VocabEntry.objects.create(entry='probar', language='es')

        VocabContextEntry.objects.create(
            vocab_context=self.vocab_context,
            vocab_entry=vocab_entry_en_1
        )
        VocabContextEntry.objects.create(
            vocab_context=self.vocab_context_2,
            vocab_entry=vocab_entry_en_1
        )
        VocabContextEntry.objects.create(
            vocab_context=self.vocab_context,
            vocab_entry=vocab_entry_en_2
        )
        VocabContextEntry.objects.create(
            vocab_context=self.vocab_context,
            vocab_entry=vocab_entry_es_1
        )

        language = self.vocab_context_entry_manager.source_entry_language_max(self.vocab_source.id)
        self.assertEqual(language, 'en')
