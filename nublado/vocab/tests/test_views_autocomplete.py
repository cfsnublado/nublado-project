import json

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.views.generic import View

from core.views import AutocompleteMixin
from ..models import (
    VocabContext, VocabContextEntry, VocabEntry,
    VocabSource
)
from ..views.views_vocab_autocomplete import (
    VocabEntryAutocompleteView,
    VocabSourceAutocompleteView, VocabSourceEntryAutocompleteView
)

User = get_user_model()


class TestCommon(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_user(
            username='cfs',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@foo.com',
            password=self.pwd
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)

    def add_session_to_request(self, request):
        '''Annotate a request object with a session'''
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()


class VocabSourceAutocompleteViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceAutocompleteViewTest, self).setUp()
        self.vocab_source_1 = VocabSource.objects.create(
            creator=self.user,
            name='test source 1'
        )
        self.vocab_source_2 = VocabSource.objects.create(
            creator=self.user,
            name='test source 2'
        )
        self.vocab_source_3 = VocabSource.objects.create(
            creator=self.user,
            name='test source 3'
        )

    def get_autocomplete_results(self, term=None):
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        response = self.client.get(
            '{0}?term={1}'.format(
                reverse(
                    'vocab:vocab_source_autocomplete'
                ),
                term
            ),
            **kwargs
        )
        return json.loads(response.content)

    def test_inheritance(self):
        classes = (
            AutocompleteMixin,
            View
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(VocabSourceAutocompleteView, class_name)
            )

    def test_get_results(self):
        results = self.get_autocomplete_results(term='test')
        expected_results = [
            {
                'id': self.vocab_source_1.id,
                'label': self.vocab_source_1.name,
                'value': self.vocab_source_1.name,
            },
            {
                'id': self.vocab_source_2.id,
                'label': self.vocab_source_2.name,
                'value': self.vocab_source_2.name
            },
            {
                'id': self.vocab_source_3.id,
                'label': self.vocab_source_3.name,
                'value': self.vocab_source_3.name
            }
        ]
        self.assertCountEqual(results, expected_results)


class VocabEntryAutocompleteViewTest(TestCommon):

    def setUp(self):
        super(VocabEntryAutocompleteViewTest, self).setUp()
        self.vocab_entry_en_1 = VocabEntry.objects.create(language='en', entry='abstract')
        self.vocab_entry_en_2 = VocabEntry.objects.create(language='en', entry='able')
        self.vocab_entry_es_1 = VocabEntry.objects.create(language='es', entry='absolver')

    def get_autocomplete_results(self, language=None, term=None):
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        if language:
            url = reverse(
                'vocab:vocab_entry_language_autocomplete',
                kwargs={'language': language}
            )
        else:
            url = reverse('vocab:vocab_entry_autocomplete')
        response = self.client.get(
            '{0}?term={1}'.format(url, term),
            **kwargs
        )
        return json.loads(response.content)

    def test_inheritance(self):
        classes = (
            AutocompleteMixin,
            View
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntryAutocompleteView, class_name))

    def test_get_results_no_language(self):
        results = self.get_autocomplete_results(term='ab')
        expected_results = [
            {
                'id': self.vocab_entry_en_1.id,
                'label': '{0} - {1}'.format(self.vocab_entry_en_1.language, self.vocab_entry_en_1.entry),
                'value': self.vocab_entry_en_1.entry,
                'attr': {'language': self.vocab_entry_en_1.language}
            },
            {
                'id': self.vocab_entry_en_2.id,
                'label': '{0} - {1}'.format(self.vocab_entry_en_2.language, self.vocab_entry_en_2.entry),
                'value': self.vocab_entry_en_2.entry,
                'attr': {'language': self.vocab_entry_en_2.language}
            },
            {
                'id': self.vocab_entry_es_1.id,
                'label': '{0} - {1}'.format(self.vocab_entry_es_1.language, self.vocab_entry_es_1.entry),
                'value': self.vocab_entry_es_1.entry,
                'attr': {'language': self.vocab_entry_es_1.language}
            },
        ]
        self.assertCountEqual(results, expected_results)

    def test_get_results_language(self):
        # English
        results = self.get_autocomplete_results(language='en', term='ab')
        expected_results = [
            {
                'id': self.vocab_entry_en_1.id,
                'label': '{0} - {1}'.format(self.vocab_entry_en_1.language, self.vocab_entry_en_1.entry),
                'value': self.vocab_entry_en_1.entry,
                'attr': {'language': self.vocab_entry_en_1.language}
            },
            {
                'id': self.vocab_entry_en_2.id,
                'label': '{0} - {1}'.format(self.vocab_entry_en_2.language, self.vocab_entry_en_2.entry),
                'value': self.vocab_entry_en_2.entry,
                'attr': {'language': self.vocab_entry_en_2.language}
            }
        ]
        self.assertCountEqual(results, expected_results)

        # Spanish
        results = self.get_autocomplete_results(language='es', term='ab')
        expected_results = [
            {
                'id': self.vocab_entry_es_1.id,
                'label': '{0} - {1}'.format(self.vocab_entry_es_1.language, self.vocab_entry_es_1.entry),
                'value': self.vocab_entry_es_1.entry,
                'attr': {'language': self.vocab_entry_es_1.language}
            }
        ]
        self.assertCountEqual(results, expected_results)


class VocabSourceEntryAutocompleteViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceEntryAutocompleteViewTest, self).setUp()
        self.vocab_source_1 = VocabSource.objects.create(
            creator=self.user,
            name='test source 1'
        )
        self.vocab_source_2 = VocabSource.objects.create(
            creator=self.user,
            name='test source 2'
        )
        self.vocab_context_1 = VocabContext.objects.create(
            vocab_source=self.vocab_source_1,
            content='Tergiversar lo ya tergiversado es terco.'
        )
        self.vocab_context_2 = VocabContext.objects.create(
            vocab_source=self.vocab_source_2,
            content='La ternura es asombrosa.'
        )
        self.vocab_entry_1 = VocabEntry.objects.create(
            language='es',
            entry='tergiversar'
        )
        self.vocab_entry_2 = VocabEntry.objects.create(
            language='es',
            entry='terco'
        )
        self.vocab_entry_3 = VocabEntry.objects.create(
            language='es',
            entry='ternura'
        )
        self.vocab_entry_4 = VocabEntry.objects.create(
            language='en',
            entry='tertiary'
        )
        self.vocab_entry_5 = VocabEntry.objects.create(
            language='en',
            entry='terrible'
        )
        self.vocab_context_entry_1 = VocabContextEntry.objects.create(
            vocab_context=self.vocab_context_1,
            vocab_entry=self.vocab_entry_1
        )
        self.vocab_context_entry_2 = VocabContextEntry.objects.create(
            vocab_context=self.vocab_context_1,
            vocab_entry=self.vocab_entry_2
        )
        self.vocab_context_entry_3 = VocabContextEntry.objects.create(
            vocab_context=self.vocab_context_1,
            vocab_entry=self.vocab_entry_4
        )
        self.vocab_context_entry_4 = VocabContextEntry.objects.create(
            vocab_context=self.vocab_context_2,
            vocab_entry=self.vocab_entry_3
        )
        self.vocab_context_entry_4 = VocabContextEntry.objects.create(
            vocab_context=self.vocab_context_2,
            vocab_entry=self.vocab_entry_5
        )

    def get_autocomplete_results(self, source_pk=None, language=None, term=None):
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        if language:
            url = reverse(
                'vocab:vocab_source_entry_language_autocomplete',
                kwargs={
                    'vocab_source_pk': source_pk,
                    'language': language
                }
            )
        else:
            url = reverse(
                'vocab:vocab_source_entry_autocomplete',
                kwargs={'vocab_source_pk': source_pk}
            )
        response = self.client.get(
            '{0}?term={1}'.format(url, term),
            **kwargs
        )
        return json.loads(response.content)

    def test_inheritance(self):
        classes = (
            AutocompleteMixin,
            View
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(VocabSourceEntryAutocompleteView, class_name)
            )

    def test_get_results(self):
        # Source 1
        results = self.get_autocomplete_results(source_pk=self.vocab_source_1.id, term='ter')
        expected_results = [
            {
                'id': self.vocab_entry_1.id,
                'label': '{0} - {1}'.format(self.vocab_entry_1.language, self.vocab_entry_1.entry),
                'value': self.vocab_entry_1.entry,
                'attr': {'language': self.vocab_entry_1.language}
            },
            {
                'id': self.vocab_entry_2.id,
                'label': '{0} - {1}'.format(self.vocab_entry_2.language, self.vocab_entry_2.entry),
                'value': self.vocab_entry_2.entry,
                'attr': {'language': self.vocab_entry_2.language}
            },
            {
                'id': self.vocab_entry_4.id,
                'label': '{0} - {1}'.format(self.vocab_entry_4.language, self.vocab_entry_4.entry),
                'value': self.vocab_entry_4.entry,
                'attr': {'language': self.vocab_entry_4.language}
            }
        ]
        self.assertCountEqual(results, expected_results)

        # Source 2
        results = self.get_autocomplete_results(source_pk=self.vocab_source_2.id, term='ter')
        expected_results = [
            {
                'id': self.vocab_entry_3.id,
                'label': '{0} - {1}'.format(self.vocab_entry_3.language, self.vocab_entry_3.entry),
                'value': self.vocab_entry_3.entry,
                'attr': {'language': self.vocab_entry_3.language}
            },
            {
                'id': self.vocab_entry_5.id,
                'label': '{0} - {1}'.format(self.vocab_entry_5.language, self.vocab_entry_5.entry),
                'value': self.vocab_entry_5.entry,
                'attr': {'language': self.vocab_entry_5.language}
            }
        ]
        self.assertCountEqual(results, expected_results)

    def test_get_results_language(self):
        # Source 1
        results = self.get_autocomplete_results(
            source_pk=self.vocab_source_1.id,
            language='es',
            term='ter'
        )
        expected_results = [
            {
                'id': self.vocab_entry_1.id,
                'label': '{0} - {1}'.format(self.vocab_entry_1.language, self.vocab_entry_1.entry),
                'value': self.vocab_entry_1.entry,
                'attr': {'language': self.vocab_entry_1.language}
            },
            {
                'id': self.vocab_entry_2.id,
                'label': '{0} - {1}'.format(self.vocab_entry_2.language, self.vocab_entry_2.entry),
                'value': self.vocab_entry_2.entry,
                'attr': {'language': self.vocab_entry_2.language}
            }
        ]
        self.assertCountEqual(results, expected_results)

        # Source 2
        results = self.get_autocomplete_results(
            source_pk=self.vocab_source_2.id,
            language='es',
            term='ter'
        )
        expected_results = [
            {
                'id': self.vocab_entry_3.id,
                'label': '{0} - {1}'.format(self.vocab_entry_3.language, self.vocab_entry_3.entry),
                'value': self.vocab_entry_3.entry,
                'attr': {'language': self.vocab_entry_3.language}
            }
        ]
        self.assertCountEqual(results, expected_results)
