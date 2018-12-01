import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.views.generic import ListView, View
from django.urls import resolve, reverse

from core.utils import FuzzyInt
from core.views import AutocompleteMixin
from ..models import (
    VocabContext, VocabContextEntry, VocabEntry,
    VocabSource
)
from ..views.views_vocab_entry import (
    VocabEntryUserAutocompleteView, VocabEntryAutocompleteView,
    VocabEntrySearchView, VocabEntryUserSearchView
)

User = get_user_model()

APP_NAME = "vocab"


class TestCommon(TestCase):

    def setUp(self):
        super(TestCommon, self).setUp()
        self.pwd = "Coffee?69c"
        self.user = User.objects.create_superuser(
            username="cfs7",
            first_name="Christopher",
            last_name="Sanders",
            email="cfs7@foo.com",
            password=self.pwd
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)


class VocabEntryAutocompleteViewTest(TestCommon):

    def setUp(self):
        super(VocabEntryAutocompleteViewTest, self).setUp()
        self.vocab_entry_1 = VocabEntry.objects.create(creator=self.user, entry="apple")
        self.vocab_entry_2 = VocabEntry.objects.create(creator=self.user, entry="appal")
        self.vocab_entry_3 = VocabEntry.objects.create(creator=self.user, entry="apply")
        self.vocab_entry_4 = VocabEntry.objects.create(creator=self.user, entry="blue")
        self.vocab_entry_5 = VocabEntry.objects.create(creator=self.user, entry="beer")
        self.vocab_entry_6 = VocabEntry.objects.create(creator=self.user, entry="extemporaneous speaking")

    def test_inheritance(self):
        classes = (
            AutocompleteMixin,
            View
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntryAutocompleteView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse("vocab:vocab_entry_autocomplete"))
        self.assertEqual(
            found.func.__name__,
            VocabEntryAutocompleteView.as_view().__name__
        )

    def test_autocomplete_results(self):
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        search_term = "App"
        response = self.client.get(
            reverse("vocab:vocab_entry_autocomplete"),
            data={"term": search_term},
            **kwargs
        )
        json_string = response.content.decode("utf-8")
        response_data = json.loads(json_string)
        expected_data = [
            {
                "id": self.vocab_entry_1.id,
                "label": "{0} - {1}".format(self.vocab_entry_1.language, self.vocab_entry_1.entry),
                "value": self.vocab_entry_1.entry,
                "attr": {"language": self.vocab_entry_1.language}
            },
            {
                "id": self.vocab_entry_2.id,
                "label": "{0} - {1}".format(self.vocab_entry_2.language, self.vocab_entry_2.entry),
                "value": self.vocab_entry_2.entry,
                "attr": {"language": self.vocab_entry_2.language}
            },
            {
                "id": self.vocab_entry_3.id,
                "label": "{0} - {1}".format(self.vocab_entry_3.language, self.vocab_entry_3.entry),
                "value": self.vocab_entry_3.entry,
                "attr": {"language": self.vocab_entry_3.language}
            },

        ]
        self.assertEquals(3, len(response_data))
        self.assertCountEqual(expected_data, response_data)

        search_term = "Ext"
        response = self.client.get(
            reverse("vocab:vocab_entry_autocomplete"),
            data={"term": search_term},
            **kwargs
        )
        json_string = response.content.decode("utf-8")
        response_data = json.loads(json_string)
        expected_data = [
            {
                "id": self.vocab_entry_6.id,
                "label": "{0} - {1}".format(self.vocab_entry_6.language, self.vocab_entry_6.entry),
                "value": self.vocab_entry_6.entry,
                "attr": {"language": self.vocab_entry_6.language}
            }
        ]
        self.assertEquals(1, len(response_data))
        self.assertCountEqual(expected_data, response_data)

    def test_num_queries(self):
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        search_term = "app"
        with self.assertNumQueries(FuzzyInt(1, 3)):
            self.client.get(
                reverse("vocab:vocab_entry_autocomplete"),
                data={"term": search_term},
                **kwargs
            )


class VocabEntryUserAutocompleteViewTest(TestCommon):

    def setUp(self):
        super(VocabEntryUserAutocompleteViewTest, self).setUp()
        self.user_2 = User.objects.create_superuser(
            username="kfl7",
            first_name="Karen",
            last_name="Fuentes",
            email="kfl7@foo.com",
            password=self.pwd
        )
        self.vocab_entry_1 = VocabEntry.objects.create(creator=self.user_2, entry="apple")
        self.vocab_entry_2 = VocabEntry.objects.create(creator=self.user_2, entry="appal")
        self.vocab_entry_3 = VocabEntry.objects.create(creator=self.user, entry="apply")
        self.vocab_entry_4 = VocabEntry.objects.create(creator=self.user, entry="blue")
        self.vocab_entry_5 = VocabEntry.objects.create(creator=self.user, entry="beer")
        self.vocab_entry_6 = VocabEntry.objects.create(creator=self.user, entry="extemporaneous speaking")
        self.vocab_entry_7 = VocabEntry.objects.create(creator=self.user, entry="extra helping")
        self.vocab_entry_8 = VocabEntry.objects.create(creator=self.user_2, entry="extraneous")

    def test_inheritance(self):
        classes = (
            VocabEntryAutocompleteView,
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntryUserAutocompleteView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse("vocab:vocab_entry_autocomplete"))
        self.assertEqual(
            found.func.__name__,
            VocabEntryAutocompleteView.as_view().__name__
        )

    def test_autocomplete_results(self):
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        search_term = "App"
        # cfs7: apply
        # kfl7: apple, appal

        self.login_test_user(username="cfs7")
        response = self.client.get(
            reverse(
                "vocab:vocab_entry_user_autocomplete",
                kwargs={"language": "en", "user_pk": self.user.id},
            ),
            data={"term": search_term},
            **kwargs
        )
        json_string = response.content.decode("utf-8")
        response_data = json.loads(json_string)
        expected_data = [
            {
                "id": self.vocab_entry_3.id,
                "label": "{0} - {1}".format(self.vocab_entry_3.language, self.vocab_entry_3.entry),
                "value": self.vocab_entry_3.entry,
                "attr": {"language": self.vocab_entry_3.language}
            },

        ]
        self.assertEquals(1, len(response_data))
        self.assertCountEqual(expected_data, response_data)

        self.login_test_user(username="kfl7")
        response = self.client.get(
            reverse(
                "vocab:vocab_entry_user_autocomplete",
                kwargs={"language": "en", "user_pk": self.user_2.id},
            ),
            data={"term": search_term},
            **kwargs
        )
        json_string = response.content.decode("utf-8")
        response_data = json.loads(json_string)
        expected_data = [
            {
                "id": self.vocab_entry_1.id,
                "label": "{0} - {1}".format(self.vocab_entry_1.language, self.vocab_entry_1.entry),
                "value": self.vocab_entry_1.entry,
                "attr": {"language": self.vocab_entry_1.language}
            },
            {
                "id": self.vocab_entry_2.id,
                "label": "{0} - {1}".format(self.vocab_entry_2.language, self.vocab_entry_2.entry),
                "value": self.vocab_entry_2.entry,
                "attr": {"language": self.vocab_entry_2.language}
            },
        ]
        self.assertEquals(2, len(response_data))
        self.assertCountEqual(expected_data, response_data)

        search_term = "Ext"
        # cfs7: extemporaneous speaking, extra helping
        # kfl7: extraneous

        self.login_test_user(username="cfs7")
        response = self.client.get(
            reverse(
                "vocab:vocab_entry_user_autocomplete",
                kwargs={"language": "en", "user_pk": self.user.id},
            ),
            data={"term": search_term},
            **kwargs
        )
        json_string = response.content.decode("utf-8")
        response_data = json.loads(json_string)
        expected_data = [
            {
                "id": self.vocab_entry_6.id,
                "label": "{0} - {1}".format(self.vocab_entry_6.language, self.vocab_entry_6.entry),
                "value": self.vocab_entry_6.entry,
                "attr": {"language": self.vocab_entry_6.language}
            },
            {
                "id": self.vocab_entry_7.id,
                "label": "{0} - {1}".format(self.vocab_entry_7.language, self.vocab_entry_7.entry),
                "value": self.vocab_entry_7.entry,
                "attr": {"language": self.vocab_entry_7.language}
            }
        ]
        self.assertEquals(2, len(response_data))
        self.assertCountEqual(expected_data, response_data)

        self.login_test_user(username="kfl7")
        response = self.client.get(
            reverse(
                "vocab:vocab_entry_user_autocomplete",
                kwargs={"language": "en", "user_pk": self.user_2.id},
            ),
            data={"term": search_term},
            **kwargs
        )
        json_string = response.content.decode("utf-8")
        response_data = json.loads(json_string)
        expected_data = [
            {
                "id": self.vocab_entry_8.id,
                "label": "{0} - {1}".format(self.vocab_entry_8.language, self.vocab_entry_8.entry),
                "value": self.vocab_entry_8.entry,
                "attr": {"language": self.vocab_entry_8.language}
            }
        ]
        self.assertEquals(1, len(response_data))
        self.assertCountEqual(expected_data, response_data)

    def test_num_queries(self):
        self.login_test_user(username="cfs7")
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        search_term = "app"
        with self.assertNumQueries(FuzzyInt(1, 3)):
            self.client.get(
                reverse(
                    "vocab:vocab_entry_user_autocomplete",
                    kwargs={"language": "en", "user_pk": self.user.id},
                ),
                data={"term": search_term},
                **kwargs
            )


class VocabEntryUserSearchViewTest(TestCommon):

    def setUp(self):
        super(VocabEntryUserSearchViewTest, self).setUp()
        self.vocab_entry_1 = VocabEntry.objects.create(creator=self.user, entry="world")
        self.vocab_entry_2 = VocabEntry.objects.create(creator=self.user, entry="chaos")
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="Test source"
        )

    def add_contexts(self):
        for i in range(10):
            vocab_context = VocabContext.objects.create(
                vocab_source=self.vocab_source,
                content="The world is a big place full of chaotic worlds within themselves."
            )
            vocab_context_entry = VocabContextEntry.objects.create(
                vocab_context=vocab_context,
                vocab_entry=self.vocab_entry_1
            )
            vocab_context_entry.add_vocab_entry_tag("world")

    def test_inheritance(self):
        classes = (
            ListView,
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntrySearchView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                "vocab:vocab_entry_user_search",
                kwargs={"username": self.user.username}
            )
        )
        self.assertEqual(
            found.func.__name__,
            VocabEntryUserSearchView.as_view().__name__
        )

    def test_view_renders_correct_template(self):
        response = self.client.get(
            reverse(
                "vocab:vocab_entry_user_search",
                kwargs={"username": self.user.username}
            )
        )
        self.assertTemplateUsed(response, "{0}/vocab_entry_search.html".format(APP_NAME))

    def test_view_search_results(self):
        self.add_contexts()
        response = self.client.get(
            reverse(
                "vocab:vocab_entry_user_search",
                kwargs={"username": self.user.username}
            ),
            {
                "entry": self.vocab_entry_1.entry,
                "language": self.vocab_entry_1.language
            }
        )
        self.assertEqual(len(response.context["vocab_context_entries"]), 10)
        self.assertEqual(response.context["vocab_entry"], self.vocab_entry_1)

        # Default search language is en.
        response = self.client.get(
            reverse(
                "vocab:vocab_entry_user_search",
                kwargs={"username": self.user.username}
            ),
            {"entry": self.vocab_entry_1.entry}
        )
        self.assertEqual(len(response.context["vocab_context_entries"]), 10)
        self.assertEqual(response.context["search_language"], "en")
        self.assertEqual(response.context["vocab_entry"], self.vocab_entry_1)

        # No results with no arguments.
        response = self.client.get(
            reverse(
                "vocab:vocab_entry_user_search",
                kwargs={"username": self.user.username}
            )
        )
        self.assertEqual(len(response.context["vocab_context_entries"]), 0)
        self.assertIsNone(response.context["vocab_entry"])

    def test_num_queries(self):
        self.add_contexts()
        with self.assertNumQueries(FuzzyInt(1, 9)):
            self.client.get(
                reverse(
                    "vocab:vocab_entry_user_search",
                    kwargs={"username": self.user.username}
                ),
                {
                    "entry": self.vocab_entry_1.entry,
                    "language": self.vocab_entry_1.language
                }
            )
