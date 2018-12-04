import json

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.views.generic import DetailView, View

from core.utils import setup_test_view
from core.views import AutocompleteMixin, CachedObjectMixin
from ..models import VocabEntry, VocabProject, VocabSource
from ..views.views_mixins import (
    VocabEntryMixin, VocabEntryPermissionMixin, VocabEntrySessionMixin,
    VocabProjectMixin, VocabProjectSessionMixin,
    VocabSourceMixin, VocabSourcePermissionMixin, VocabSourceSessionMixin
)
from ..views.views_vocab_autocomplete import (
    VocabEntryAutocompleteView, VocabProjectSourceAutocompleteView,
    VocabSourceAutocompleteView
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


class VocabProjectSourceAutocompleteViewTest(TestCommon):

    def setUp(self):
        super(VocabProjectSourceAutocompleteViewTest, self).setUp()
        self.vocab_project_1 = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_project_2 = VocabProject.objects.create(
            owner=self.user,
            name='test project 2'
        )
        self.vocab_source_1 = VocabSource.objects.create(
            vocab_project=self.vocab_project_1,
            creator=self.user,
            name='test source 1'
        )
        self.vocab_source_2 = VocabSource.objects.create(
            vocab_project=self.vocab_project_1,
            creator=self.user,
            name='test source 2'
        )
        self.vocab_source_3 = VocabSource.objects.create(
            vocab_project=self.vocab_project_2,
            creator=self.user,
            name='test source 3'
        )

    def test_inheritance(self):
        classes = (
            VocabSourceAutocompleteView,
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(VocabProjectSourceAutocompleteView, class_name)
            )

    def test_get_results(self):
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

        # Project 1
        response = self.client.get(
            '{0}?term={1}'.format(
                reverse(
                    'vocab:vocab_project_source_autocomplete',
                    kwargs={'vocab_project_pk': self.vocab_project_1.id}
                ),
                'test'
            ),
            **kwargs
        )
        results = json.loads(response.content)
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
            }
        ]
        self.assertCountEqual(results, expected_results)

        # Project 2
        response = self.client.get(
            '{0}?term={1}'.format(
                reverse(
                    'vocab:vocab_project_source_autocomplete',
                    kwargs={'vocab_project_pk': self.vocab_project_2.id}
                ),
                'test'
            ),
            **kwargs
        )
        results = json.loads(response.content)
        expected_results = [
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

    def test_inheritance(self):
        classes = (
            AutocompleteMixin,
            View
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntryAutocompleteView, class_name))

    def test_get_results_no_language(self):
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        response = self.client.get(
            '{0}?term={1}'.format(
                reverse('vocab:vocab_entry_autocomplete'),
                'ab'
            ),
            **kwargs
        )
        results = json.loads(response.content)
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
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

        # English
        response = self.client.get(
            '{0}?term={1}'.format(
                reverse(
                    'vocab:vocab_entry_language_autocomplete',
                    kwargs={'language': 'en'}
                ),
                'ab'
            ),
            **kwargs
        )
        results = json.loads(response.content)
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
        response = self.client.get(
            '{0}?term={1}'.format(
                reverse(
                    'vocab:vocab_entry_language_autocomplete',
                    kwargs={'language': 'es'}
                ),
                'ab'
            ),
            **kwargs
        )
        results = json.loads(response.content)
        expected_results = [
            {
                'id': self.vocab_entry_es_1.id,
                'label': '{0} - {1}'.format(self.vocab_entry_es_1.language, self.vocab_entry_es_1.entry),
                'value': self.vocab_entry_es_1.entry,
                'attr': {'language': self.vocab_entry_es_1.language}
            }
        ]
        self.assertCountEqual(results, expected_results)
