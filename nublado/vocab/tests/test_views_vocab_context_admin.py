import json

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import resolve, reverse
from django.test import RequestFactory, TestCase
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView

from core.views import AjaxDeleteMixin
from ..conf import settings
from ..forms import VocabContextCreateForm
from ..models import VocabContext, VocabSource
from ..validation import error_messages
from ..views.views_vocab_context_admin import (
    VocabContextCreateView, VocabContextDeleteView, VocabContextTagView
)
from ..views.views_mixins import VocabSourceMixin

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

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)

    def add_session_to_request(self, request):
        """Annotate a request object with a session"""
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()


class VocabContextCreateViewTest(TestCommon):

    def setUp(self):
        super(VocabContextCreateViewTest, self).setUp()
        self.vocab_context_data = {
            "content": "blah blah blah"
        }

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSourceMixin,
            CreateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabContextCreateView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse(
            "vocab_admin:vocab_context_create",
            kwargs={"vocab_source_pk": self.vocab_source.id})
        )
        self.assertEqual(found.func.__name__, VocabContextCreateView.as_view().__name__)

    def test_view_non_authenticated_user_redirected_to_login(self):
        response = self.client.get(reverse(
            "vocab_admin:vocab_context_create",
            kwargs={"vocab_source_pk": self.vocab_source.id}
        ))
        self.assertRedirects(
            response,
            expected_url="{0}?next=/admin/{1}/source/{2}/context/create/".format(
                reverse(settings.LOGIN_URL),
                URL_PREFIX,
                self.vocab_source.id
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=""
        )

    def test_view_returns_correct_status_code(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                "vocab_admin:vocab_context_create",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                "vocab_admin:vocab_context_create",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            )
        )
        self.assertTemplateUsed(response, "{0}/admin/vocab_context_create.html".format(APP_NAME))

    def test_view_uses_correct_form(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                "vocab_admin:vocab_context_create",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            )
        )
        self.assertIsInstance(response.context["form"], VocabContextCreateForm)

    def test_view_injects_form_kwargs(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                "vocab_admin:vocab_context_create",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            )
        )
        form = response.context["form"]
        self.assertEqual(form.vocab_source, self.vocab_source)

    def test_view_creates_object(self):
        self.login_test_user(self.user.username)
        self.assertFalse(
            VocabContext.objects.filter(
                vocab_source_id=self.vocab_source,
                content=self.vocab_context_data["content"]
            ).exists()
        )
        self.client.post(
            reverse(
                "vocab_admin:vocab_context_create",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            ),
            self.vocab_context_data
        )
        self.assertTrue(
            VocabContext.objects.filter(
                vocab_source_id=self.vocab_source,
                content=self.vocab_context_data["content"]
            ).exists()
        )

    def test_invalid_data_shows_form_errors_and_does_not_save(self):
        self.vocab_context_data["content"] = ""
        self.login_test_user(self.user.username)
        response = self.client.post(
            reverse(
                "vocab_admin:vocab_context_create",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            ),
            self.vocab_context_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            VocabContext.objects.filter(
                vocab_source_id=self.vocab_source,
                content=self.vocab_context_data["content"]
            ).exists()
        )
        self.assertIsInstance(response.context["form"], VocabContextCreateForm)
        self.assertFormError(response, "form", "content", error_messages["field_required"])

    def test_view_redirects_on_success(self):
        self.login_test_user(self.user.username)
        response = self.client.post(
            reverse(
                "vocab_admin:vocab_context_create",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            ),
            self.vocab_context_data
        )
        vocab_context = VocabContext.objects.get(
            content=self.vocab_context_data["content"]
        )
        self.assertRedirects(
            response,
            expected_url=reverse("vocab_admin:vocab_context_tag", kwargs={"pk": vocab_context.id}),
            status_code=302,
            target_status_code=200,
            msg_prefix=""
        )


class VocabContextTagViewTest(TestCommon):

    def setUp(self):
        super(VocabContextTagViewTest, self).setUp()
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="Hello hello"
        )

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSourceMixin,
            DetailView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabContextTagView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse(
            "vocab_admin:vocab_context_tag",
            kwargs={"pk": self.vocab_context.id})
        )
        self.assertEqual(found.func.__name__, VocabContextTagView.as_view().__name__)


class VocabContextDeleteViewTest(TestCommon):

    def setUp(self):
        super(VocabContextDeleteViewTest, self).setUp()
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="Hello hello"
        )

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            AjaxDeleteMixin,
            DeleteView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabContextDeleteView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse(
            "vocab_admin:vocab_context_delete",
            kwargs={"pk": self.vocab_context.id})
        )
        self.assertEqual(found.func.__name__, VocabContextDeleteView.as_view().__name__)

    def test_view_non_authenticated_user_redirected_to_login(self):
        response = self.client.get(
            reverse("vocab_admin:vocab_context_delete", kwargs={"pk": self.vocab_context.id})
        )
        self.assertRedirects(
            response,
            expected_url="{url}?next=/admin/{module}/context/{pk}/delete/".format(
                url=reverse(settings.LOGIN_URL),
                module=URL_PREFIX,
                pk=self.vocab_context.id
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=""
        )

    def test_view_returns_correct_status_code(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse("vocab_admin:vocab_context_delete", kwargs={"pk": self.vocab_context.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse("vocab_admin:vocab_context_delete", kwargs={"pk": self.vocab_context.id})
        )
        self.assertTemplateUsed(response, "{0}/admin/vocab_context_delete_confirm.html".format(APP_NAME))

    def test_view_deletes_object(self):
        self.login_test_user(self.user.username)
        obj_id = self.vocab_context.id
        self.assertTrue(VocabContext.objects.filter(pk=obj_id).exists())
        self.client.post(
            reverse("vocab_admin:vocab_context_delete", kwargs={"pk": obj_id})
        )
        self.assertFalse(VocabContext.objects.filter(pk=obj_id).exists())

    def test_view_redirects_on_success(self):
        self.login_test_user(self.user.username)
        response = self.client.post(
            reverse("vocab_admin:vocab_context_delete", kwargs={"pk": self.vocab_context.id})
        )
        self.assertRedirects(
            response,
            expected_url=reverse(settings.PROJECT_HOME_URL),
            status_code=302,
            target_status_code=200,
            msg_prefix=""
        )

    def test_view_ajax(self):
        self.login_test_user(self.user.username)
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        obj_id = self.vocab_context.id
        self.assertTrue(VocabContext.objects.filter(pk=obj_id).exists())
        response = self.client.post(
            reverse("vocab_admin:vocab_context_delete", kwargs={"pk": obj_id}),
            **kwargs
        )
        self.assertEqual(response.status_code, 200)
        json_string = response.content.decode("utf-8")
        response_data = json.loads(json_string)
        self.assertEqual(_("message_success"), response_data["success_message"])
        self.assertFalse(VocabContext.objects.filter(pk=obj_id).exists())
