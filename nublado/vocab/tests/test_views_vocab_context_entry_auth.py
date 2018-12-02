from django.contrib.auth import get_user_model
from django.urls import resolve, reverse
from django.test import RequestFactory, TestCase

from ..conf import settings
from ..models import (
    VocabEntry, VocabContext, VocabContextEntry,
    VocabProject, VocabSource
)
from ..views.views_vocab_source_auth import VocabSourceEntriesView

User = get_user_model()

APP_NAME = 'vocab'
URL_PREFIX = getattr(settings, 'VOCAB_URL_PREFIX')


class TestCommon(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
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
            name='Test Source'
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='This is a test context. I like contexts.'
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)


# class VocabContextEntryListViewTest(TestCommon):

#     def setUp(self):
#         super(VocabContextEntryListViewTest, self).setUp()
#         self.vocab_entry = VocabEntry.objects.create(creator=self.user, entry='hello')
#         self.vocab_context_2 = VocabContext.objects.create(
#             vocab_source=self.vocab_source,
#             content='This is another test context. I like contexts.'
#         )
#         VocabContextEntry.objects.create(
#             vocab_context=self.vocab_context,
#             vocab_entry=self.vocab_entry
#         )
#         VocabContextEntry.objects.create(
#             vocab_context=self.vocab_context_2,
#             vocab_entry=self.vocab_entry
#         )

#     def test_inheritance(self):
#         classes = (
#             LoginRequiredMixin,
#             VocabEntryMixin,
#             ListView
#         )
#         for class_name in classes:
#             self.assertTrue(issubclass(VocabContextEntryListView, class_name))

#     def test_correct_view_used(self):
#         found = resolve(
#             reverse('vocab:vocab_context_entries', kwargs={'vocab_entry_slug': self.vocab_entry.slug})
#         )
#         self.assertEqual(found.func.__name__, VocabContextEntryListView.as_view().__name__)

#     def test_view_non_authenticated_user_redirected_to_login(self):
#         response = self.client.get(
#             reverse(
#                 'vocab:vocab_context_entries',
#                 kwargs={'vocab_entry_slug': self.vocab_entry.slug}
#             )
#         )
#         self.assertRedirects(
#             response,
#             expected_url='{0}?next=/vocab/contexts/{1}/'.format(
#                 reverse(settings.LOGIN_URL),
#                 self.vocab_entry.slug
#             ),
#             status_code=302,
#             target_status_code=200,
#             msg_prefix=''
#         )

#     def test_view_renders_correct_template(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(
#             reverse(
#                 'vocab:vocab_context_entries',
#                 kwargs={'vocab_entry_slug': self.vocab_entry.slug}
#             )
#         )
#         self.assertTemplateUsed(response, '{0}/vocab/admin/vocab_context_entries.html'.format(APP_NAME))

#     def test_num_queries(self):
#         self.login_test_user(self.user.username)
#         with self.assertNumQueries(9):
#             self.client.get(
#                 reverse(
#                     'vocab:vocab_context_entries',
#                     kwargs={'vocab_entry_slug': self.vocab_entry.slug}
#                 )
#             )

