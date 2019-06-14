from django.contrib.auth import get_user_model
from django.test import TestCase
from django.views.generic import TemplateView
from django.urls import resolve, reverse

from core.views import ObjectSessionMixin
from ..views.views_mixins import (
    VocabEntryMixin, VocabEntrySearchMixin, VocabEntrySessionMixin
)
from ..views.views_vocab_entry import VocabEntriesView, VocabEntryView

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


class VocabEntriesViewTest(TestCommon):

    def setUp(self):
        super(VocabEntriesViewTest, self).setUp()

    def test_inheritance(self):
        classes = (
            ObjectSessionMixin,
            VocabEntrySearchMixin,
            TemplateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntriesView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse('vocab:vocab_entries'))
        self.assertEqual(found.func.__name__, VocabEntriesView.as_view().__name__)

    def test_view_returns_correct_status_code(self):
        response = self.client.get(reverse('vocab:vocab_entries'))
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get(reverse('vocab:vocab_entries'))
        self.assertTemplateUsed(response, '{0}/vocab_entries.html'.format(APP_NAME))


class VocabEntryViewTest(TestCommon):

    def setUp(self):
        super(VocabEntryViewTest, self).setUp()

    def test_inheritance(self):
        classes = (
            VocabEntrySessionMixin,
            VocabEntryMixin,
            TemplateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntryView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse('vocab:vocab_entries'))
        self.assertEqual(found.func.__name__, VocabEntriesView.as_view().__name__)

    def test_view_returns_correct_status_code(self):
        response = self.client.get(reverse('vocab:vocab_entries'))
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get(reverse('vocab:vocab_entries'))
        self.assertTemplateUsed(response, '{0}/vocab_entries.html'.format(APP_NAME))
