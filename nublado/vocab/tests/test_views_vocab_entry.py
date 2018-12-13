from django.contrib.auth import get_user_model
from django.test import TestCase
from django.views.generic import TemplateView
from django.urls import resolve, reverse

from core.utils import FuzzyInt
from core.views import ObjectSessionMixin
from ..models import (
    VocabContext, VocabContextEntry, VocabEntry,
    VocabProject, VocabSource
)
from ..views.views_vocab_entry import (
    VocabEntrySearchView
)
from ..views.views_mixins import VocabEntrySearchMixin

User = get_user_model()

APP_NAME = 'vocab'


class TestCommon(TestCase):

    def setUp(self):
        super(TestCommon, self).setUp()
        self.pwd = 'Coffee?69c'
        self.user = User.objects.create_superuser(
            username='cfs7',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@foo.com',
            password=self.pwd
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)


class VocabEntrySearchViewTest(TestCommon):

    def setUp(self):
        super(VocabEntrySearchViewTest, self).setUp()
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='Test source'
        )

    def test_inheritance(self):
        classes = (
            VocabEntrySearchMixin,
            ObjectSessionMixin,
            TemplateView,
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntrySearchView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse('vocab:vocab_entry_search')
        )
        self.assertEqual(
            found.func.__name__,
            VocabEntrySearchView.as_view().__name__
        )

    def test_view_renders_correct_template(self):
        response = self.client.get(
            reverse('vocab:vocab_entry_search')
        )
        self.assertTemplateUsed(response, '{0}/vocab_search.html'.format(APP_NAME))

    def test_view_search_no_success(self):
        response = self.client.get(
            reverse('vocab:vocab_entry_search'),
            {
                'search_language': 'en',
                'search_entry': 'foo'
            }
        )
        self.assertIsNone(response.context['vocab_entry'])
        self.assertIsNone(response.context['vocab_entry_contexts'])

    def test_view_search_success(self):
        vocab_entry = VocabEntry.objects.create(
            language='en',
            entry='world'
        )
        vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='The world is chaotic.'
        )
        vocab_context_entry = VocabContextEntry.objects.create(
            vocab_context=vocab_context,
            vocab_entry=vocab_entry
        )
        response = self.client.get(
            reverse('vocab:vocab_entry_search'),
            {
                'search_language': vocab_entry.language,
                'search_entry': vocab_entry.entry
            }
        )
        vocab_entry_contexts = response.context['vocab_entry_contexts']
        self.assertEqual(vocab_entry, response.context['vocab_entry'])
        self.assertEqual(1, vocab_entry_contexts.count())
        self.assertEqual(vocab_context_entry, vocab_entry_contexts[0])

    def test_num_queries(self):
        response = None
        vocab_entry = VocabEntry.objects.create(
            language='en',
            entry='world'
        )
        for x in range(0, 20):
            vocab_context = VocabContext.objects.create(
                vocab_source=self.vocab_source,
                content='The world is chaotic.'
            )
            VocabContextEntry.objects.create(
                vocab_context=vocab_context,
                vocab_entry=vocab_entry
            )
        with self.assertNumQueries(FuzzyInt(1, 9)):
            response = self.client.get(
                reverse(
                    'vocab:vocab_entry_search',
                ),
                {
                    'search_language': vocab_entry.language,
                    'search_entry': vocab_entry.entry
                }
            )
        self.assertEqual(20, response.context['vocab_entry_contexts'].count())
