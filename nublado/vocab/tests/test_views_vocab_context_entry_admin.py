from django.contrib.auth import get_user_model
from django.urls import resolve, reverse
from django.test import RequestFactory, TestCase

from ..conf import settings
from ..models import (
    VocabEntry, VocabContext, VocabContextEntry,
    VocabSource
)
from ..views.views_vocab_source_admin import VocabSourceEntriesView

User = get_user_model()

APP_NAME = "vocab"
URL_PREFIX = getattr(settings, "VOCAB_URL_PREFIX")


class TestCommon(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.pwd = "Pizza?69p"
        self.user = User.objects.create_user(
            username="cfs7",
            first_name="Christopher",
            last_name="Sanders",
            email="cfs7@foo.com",
            password=self.pwd
        )
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="Test Source"
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="This is a test context. I like contexts."
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)


# class VocabContextEntryListViewTest(TestCommon):

#     def setUp(self):
#         super(VocabContextEntryListViewTest, self).setUp()
#         self.vocab_entry = VocabEntry.objects.create(creator=self.user, entry="hello")
#         self.vocab_context_2 = VocabContext.objects.create(
#             vocab_source=self.vocab_source,
#             content="This is another test context. I like contexts."
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
#             reverse("vocab_admin:vocab_context_entries", kwargs={"vocab_entry_slug": self.vocab_entry.slug})
#         )
#         self.assertEqual(found.func.__name__, VocabContextEntryListView.as_view().__name__)

#     def test_view_non_authenticated_user_redirected_to_login(self):
#         response = self.client.get(
#             reverse(
#                 "vocab_admin:vocab_context_entries",
#                 kwargs={"vocab_entry_slug": self.vocab_entry.slug}
#             )
#         )
#         self.assertRedirects(
#             response,
#             expected_url="{0}?next=/vocab/contexts/{1}/".format(
#                 reverse(settings.LOGIN_URL),
#                 self.vocab_entry.slug
#             ),
#             status_code=302,
#             target_status_code=200,
#             msg_prefix=""
#         )

#     def test_view_renders_correct_template(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(
#             reverse(
#                 "vocab_admin:vocab_context_entries",
#                 kwargs={"vocab_entry_slug": self.vocab_entry.slug}
#             )
#         )
#         self.assertTemplateUsed(response, "{0}/vocab/admin/vocab_context_entries.html".format(APP_NAME))

#     def test_num_queries(self):
#         self.login_test_user(self.user.username)
#         with self.assertNumQueries(9):
#             self.client.get(
#                 reverse(
#                     "vocab_admin:vocab_context_entries",
#                     kwargs={"vocab_entry_slug": self.vocab_entry.slug}
#                 )
#             )


class VocabSourceEntriesViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceEntriesViewTest, self).setUp()
        self.vocab_context_2 = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="This is another test context. I like contexts. They are nice."
        )
        self.vocab_context_3 = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="This is yet another test context. I like contexts. They are nice."
        )
        self.vocab_entry = VocabEntry.objects.create(creator=self.user, entry="hello")
        self.vocab_entry_2 = VocabEntry.objects.create(creator=self.user, entry="goodbye")

        VocabContextEntry.objects.create(
            vocab_context=self.vocab_context,
            vocab_entry=self.vocab_entry
        )
        VocabContextEntry.objects.create(
            vocab_context=self.vocab_context_2,
            vocab_entry=self.vocab_entry
        )
        VocabContextEntry.objects.create(
            vocab_context=self.vocab_context_3,
            vocab_entry=self.vocab_entry
        )
        VocabContextEntry.objects.create(
            vocab_context=self.vocab_context_3,
            vocab_entry=self.vocab_entry_2
        )

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                "vocab_admin:vocab_source_entries",
                kwargs={
                    "vocab_source_pk": self.vocab_source.id,
                    "vocab_source_slug": self.vocab_source.slug
                }
            )
        )
        self.assertEqual(found.func.__name__, VocabSourceEntriesView.as_view().__name__)

    def test_view_non_authenticated_user_ed_to_login(self):
        response = self.client.get(
            reverse(
                "vocab_admin:vocab_source_entries",
                kwargs={
                    "vocab_source_pk": self.vocab_source.id,
                    "vocab_source_slug": self.vocab_source.slug
                }
            )
        )
        self.assertRedirects(
            response,
            expected_url="{0}?next=/admin/{1}/source/{2}-{3}/entries/".format(
                reverse(settings.LOGIN_URL),
                URL_PREFIX,
                self.vocab_source.id,
                self.vocab_source.slug
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=""
        )

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                "vocab_admin:vocab_source_entries",
                kwargs={
                    "vocab_source_pk": self.vocab_source.id,
                    "vocab_source_slug": self.vocab_source.slug
                }
            )
        )
        self.assertTemplateUsed(response, "{0}/admin/vocab_source_entries.html".format(APP_NAME))

    def test_unique_entry_results(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                "vocab_admin:vocab_source_entries",
                kwargs={
                    "vocab_source_pk": self.vocab_source.id,
                    "vocab_source_slug": self.vocab_source.slug
                }
            )
        )
        vocab_entries = response.context["vocab_entries"]
        # vocab_entries with length of 2 instead of 4.
        # corresponding to the 2 distinct entries, and neglecting the duplicates.
        self.assertEqual(2, len(vocab_entries["en"]))
