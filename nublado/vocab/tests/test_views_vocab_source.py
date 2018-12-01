import json

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import resolve, reverse
from django.views.generic import View

from core.utils import FuzzyInt
from core.views import AutocompleteMixin
from ..models import VocabSource
from ..views.views_vocab_source import (
    VocabSourceAutocompleteView
)

User = get_user_model()


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


class TestCommonAutocomplete(TestCommon):

    def setUp(self):
        super(TestCommonAutocomplete, self).setUp()
        self.p1_source_1 = VocabSource.objects.create(
            creator=self.user,
            name="Physics for dummies"
        )
        self.p1_source_2 = VocabSource.objects.create(
            creator=self.user,
            name="physics review"
        )
        self.p1_source_3 = VocabSource.objects.create(
            creator=self.user,
            name="good food"
        )
        self.p1_source_4 = VocabSource.objects.create(
            creator=self.user,
            name="great food"
        )
        self.p1_source_5 = VocabSource.objects.create(
            creator=self.user,
            name="Green Spheres"
        )
        self.p2_source_1 = VocabSource.objects.create(
            creator=self.user,
            name="green drops"
        )


class VocabSourceAutocompleteViewTest(TestCommonAutocomplete):

    def setUp(self):
        super(VocabSourceAutocompleteViewTest, self).setUp()

    def test_inheritance(self):
        classes = (
            AutocompleteMixin,
            View
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(VocabSourceAutocompleteView, class_name)
            )

    def test_correct_view_used(self):
        found = resolve(reverse("vocab:vocab_source_autocomplete"))
        self.assertEqual(
            found.func.__name__,
            VocabSourceAutocompleteView.as_view().__name__
        )

    def test_autocomplete_results(self):
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        search_term = "gre"
        response = self.client.get(
            reverse("vocab:vocab_source_autocomplete"),
            data={"term": search_term},
            **kwargs
        )
        json_string = response.content.decode("utf-8")
        response_data = json.loads(json_string)
        expected_data = [
            {'id': self.p2_source_1.id, 'value': self.p2_source_1.name, 'label': self.p2_source_1.name},
            {'id': self.p1_source_5.id, 'value': self.p1_source_5.name, 'label': self.p1_source_5.name},
            {'id': self.p1_source_4.id, 'value': self.p1_source_4.name, 'label': self.p1_source_4.name},
        ]
        self.assertEquals(3, len(response_data))
        self.assertCountEqual(expected_data, response_data)

        search_term = "green"
        response = self.client.get(
            reverse("vocab:vocab_source_autocomplete"),
            data={"term": search_term},
            **kwargs
        )
        json_string = response.content.decode("utf-8")
        response_data = json.loads(json_string)
        expected_data = [
            {'id': self.p2_source_1.id, 'value': self.p2_source_1.name, 'label': self.p2_source_1.name},
            {'id': self.p1_source_5.id, 'value': self.p1_source_5.name, 'label': self.p1_source_5.name},
        ]
        self.assertEquals(2, len(response_data))
        self.assertCountEqual(expected_data, response_data)

    def test_num_queries(self):
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        search_term = "gr"
        with self.assertNumQueries(FuzzyInt(1, 3)):
            self.client.get(
                reverse("vocab:vocab_source_autocomplete"),
                data={"term": search_term},
                **kwargs
            )
