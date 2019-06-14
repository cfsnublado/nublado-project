from django.contrib.auth import get_user_model
from django.test import TestCase
from django.views.generic import TemplateView
from django.urls import resolve, reverse

from core.views import ObjectSessionMixin
from ..models import VocabProject, VocabSource
from ..views.views_mixins import (
    VocabSourceEntrySearchMixin, VocabSourceMixin,
    VocabSourceSearchMixin, VocabSourceSessionMixin
)
from ..views.views_vocab_source import (
    VocabSourceContextsView, VocabSourceDashboardView,
    VocabSourceEntriesView, VocabSourcesView
)

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


class VocabSourcesViewTest(TestCommon):

    def setUp(self):
        super(VocabSourcesViewTest, self).setUp()

    def test_inheritance(self):
        classes = (
            ObjectSessionMixin,
            VocabSourceSearchMixin,
            TemplateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourcesView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse('vocab:vocab_sources'))
        self.assertEqual(found.func.__name__, VocabSourcesView.as_view().__name__)

    def test_view_returns_correct_status_code(self):
        response = self.client.get(reverse('vocab:vocab_sources'))
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get(reverse('vocab:vocab_sources'))
        self.assertTemplateUsed(response, '{0}/vocab_sources.html'.format(APP_NAME))


class VocabSourceDashboardViewTest(TestCommon):

    def setUp(self):
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_user(
            username='cfs7',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@foo.com',
            password=self.pwd
        )
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source'
        )

    def test_inheritance(self):
        classes = (
            VocabSourceSessionMixin,
            VocabSourceMixin,
            VocabSourceEntrySearchMixin,
            TemplateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceDashboardView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                'vocab:vocab_source_dashboard',
                kwargs={
                    'vocab_source_pk': self.vocab_source.pk,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        self.assertEqual(found.func.__name__, VocabSourceDashboardView.as_view().__name__)

    def test_view_returns_correct_status_code(self):
        response = self.client.get(
            reverse(
                'vocab:vocab_source_dashboard',
                kwargs={
                    'vocab_source_pk': self.vocab_source.pk,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get(
            reverse(
                'vocab:vocab_source_dashboard',
                kwargs={
                    'vocab_source_pk': self.vocab_source.pk,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )

        self.assertTemplateUsed(response, '{0}/vocab_source_dashboard.html'.format(APP_NAME))


class VocabSourceContextsViewTest(TestCommon):

    def setUp(self):
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_user(
            username='cfs7',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@foo.com',
            password=self.pwd
        )
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source'
        )

    def test_inheritance(self):
        classes = (
            VocabSourceSessionMixin,
            VocabSourceMixin,
            VocabSourceEntrySearchMixin,
            TemplateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceContextsView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                'vocab:vocab_source_contexts',
                kwargs={
                    'vocab_source_pk': self.vocab_source.pk,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        self.assertEqual(found.func.__name__, VocabSourceContextsView.as_view().__name__)

    def test_view_returns_correct_status_code(self):
        response = self.client.get(
            reverse(
                'vocab:vocab_source_contexts',
                kwargs={
                    'vocab_source_pk': self.vocab_source.pk,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get(
            reverse(
                'vocab:vocab_source_contexts',
                kwargs={
                    'vocab_source_pk': self.vocab_source.pk,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )

        self.assertTemplateUsed(response, '{0}/vocab_source_contexts.html'.format(APP_NAME))


class VocabSourceEntriesViewTest(TestCommon):

    def setUp(self):
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_user(
            username='cfs7',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@foo.com',
            password=self.pwd
        )
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source'
        )

    def test_inheritance(self):
        classes = (
            VocabSourceSessionMixin,
            VocabSourceMixin,
            VocabSourceEntrySearchMixin,
            TemplateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceEntriesView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                'vocab:vocab_source_entries',
                kwargs={
                    'vocab_source_pk': self.vocab_source.pk,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        self.assertEqual(found.func.__name__, VocabSourceEntriesView.as_view().__name__)

    def test_view_returns_correct_status_code(self):
        response = self.client.get(
            reverse(
                'vocab:vocab_source_entries',
                kwargs={
                    'vocab_source_pk': self.vocab_source.pk,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get(
            reverse(
                'vocab:vocab_source_entries',
                kwargs={
                    'vocab_source_pk': self.vocab_source.pk,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )

        self.assertTemplateUsed(response, '{0}/vocab_source_entries.html'.format(APP_NAME))
