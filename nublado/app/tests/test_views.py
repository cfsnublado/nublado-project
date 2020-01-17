import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import resolve, reverse
from django.test import TestCase

from vocab.models import VocabEntry
from ..views import HomeView, AppSessionView

User = get_user_model()


class TestCommon(TestCase):

    def setUp(self):
        self.pwd = "Pizza?69p"
        self.user = User.objects.create_user(
            username="cfs7",
            first_name="Christopher",
            last_name="Sanders",
            email="cfs7@foo.com",
            password=self.pwd
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)


class HomeFilesTest(TestCase):

    def test_view_returns_correct_status_code(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/humans.txt')
        self.assertEqual(response.status_code, 200)


class HomeViewTest(TestCommon):

    def test_correct_view_used(self):
        found = resolve(reverse("app:home"))
        self.assertEqual(found.func.__name__, HomeView.as_view().__name__)

    def test_view_renders_correct_template(self):
        response = self.client.get(reverse("app:home"))
        self.assertTemplateUsed(response, "home.html")
        self.assertTemplateUsed(response, "base.html")

    def test_view_returns_correct_status_code(self):
        response = self.client.get(reverse("app:home"))
        self.assertEqual(response.status_code, 200)

    def test_view_context_data(self):
        response = self.client.get(reverse("app:home"))
        self.assertEqual(response.context["project_name"], settings.PROJECT_NAME)
        self.assertIsNone(response.context["random_vocab_entry"])
        v = VocabEntry.objects.create(language="en", entry="cat")
        response = self.client.get(reverse("app:home"))
        self.assertEqual(response.context["random_vocab_entry"], v)


class AppSessionViewTest(TestCase):

    def setUp(self):
        self.pwd = "Coffee?69c"
        self.user = User.objects.create_user(
            username="cfs",
            email="ChristopherSanders78@gmail.com",
            first_name="Christopher",
            last_name="Sanders",
            password=self.pwd
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)

    def test_correct_view_used(self):
        found = resolve(reverse("app:app_session"))
        self.assertEqual(found.func.__name__, AppSessionView.as_view().__name__)

    def test_view_returns_correct_status_code(self):
        self.login_test_user(username=self.user.username)
        response = self.client.post(reverse("app:app_session"))
        # Not an ajax request.
        self.assertEqual(response.status_code, 404)
        # Ajax request.
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        self.login_test_user(username=self.user.username)
        response = self.client.post(
            reverse("app:app_session"),
            json.dumps({"session_data": {}}),
            content_type="application/json",
            **kwargs
        )
        self.assertEqual(response.status_code, 200)

    def test_view_sets_session_variable(self):
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        self.login_test_user(username=self.user.username)
        self.client.post(
            reverse("app:app_session"),
            json.dumps({"session_data": {"sidebar_locked": True}}),
            content_type="application/json",
            **kwargs
        )
        session = self.client.session
        self.assertEqual(session["sidebar_locked"], True)
        self.client.post(
            reverse("app:app_session"),
            json.dumps({"session_data": {"sidebar_locked": False}}),
            content_type="application/json",
            **kwargs
        )
        session = self.client.session
        self.assertEqual(session["sidebar_locked"], False)
