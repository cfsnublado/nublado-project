import json

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import resolve, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView, DeleteView, ListView,
    TemplateView, UpdateView
)

from core.views import AjaxDeleteMixin
from core.utils import FuzzyInt
from ..conf import settings
from ..forms import VocabSourceCreateForm, VocabSourceUpdateForm
from ..models import (
    VocabEntry, VocabContext, VocabContextEntry,
    VocabSource
)
from ..validation import error_messages
from ..views.views_mixins import VocabSessionMixin, VocabSourceMixin
from ..views.views_vocab_source_admin import (
    UserVocabSourcesView, VocabSourceContextEntriesView, VocabSourceContextsView,
    VocabSourceCreateView, VocabSourceDashboardView, VocabSourceEntriesView,
    VocabSourceExportJsonView, VocabSourceDeleteView, VocabSourceUpdateView
)

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

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)

    def add_session_to_request(self, request):
        """Annotate a request object with a session"""
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()


class UserVocabSourcesViewTest(TestCommon):

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            TemplateView,
            VocabSessionMixin
        )
        for class_name in classes:
            self.assertTrue(issubclass(UserVocabSourcesView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse("vocab_admin:user_vocab_sources")
        )
        self.assertEqual(found.func.__name__, UserVocabSourcesView.as_view().__name__)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse("vocab_admin:user_vocab_sources")
        )
        self.assertTemplateUsed(response, "{0}/admin/user_vocab_sources.html".format(APP_NAME))

    def test_view_shows_only_users_sources(self):
        source_type = VocabSource.CREATED
        user_2 = User.objects.create_user(
            username="kfl7",
            first_name="Karen",
            last_name="Fuentes",
            email="kfl7@foo.com",
            password=self.pwd
        )
        for x in range(0, 4):
            VocabSource.objects.create(
                creator=self.user,
                name="source {0}".format(x),
                source_type=source_type
            )
        for x in range(0, 2):
            VocabSource.objects.create(
                creator=user_2,
                name="hello {0}".format(x),
                source_type=source_type
            )
        # user with 4 sources
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse("vocab_admin:user_vocab_sources")
        )
        sources = response.context["vocab_sources"]
        self.assertEqual(len(sources[source_type]), 4)

        # user_2 with 2 sources
        self.login_test_user(user_2.username)
        response = self.client.get(
            reverse("vocab_admin:user_vocab_sources")
        )
        sources = response.context["vocab_sources"]
        self.assertEqual(len(sources[source_type]), 2)


class VocabSourceDashboardViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceDashboardViewTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            source_type=VocabSource.BOOK,
            name="A good book"
        )

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSourceMixin,
            TemplateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceDashboardView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                "vocab_admin:vocab_source_dashboard",
                kwargs={"vocab_source_slug": self.vocab_source.slug}
            )
        )
        self.assertEqual(found.func.__name__, VocabSourceDashboardView.as_view().__name__)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                "vocab_admin:vocab_source_dashboard",
                kwargs={"vocab_source_slug": self.vocab_source.slug}
            )
        )
        self.assertTemplateUsed(response, "{0}/admin/vocab_source_dashboard.html".format(APP_NAME))


class VocabSourceCreateViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceCreateViewTest, self).setUp()
        self.vocab_source_data = {
            "source_type": VocabSource.BOOK,
            "name": "A tale of two wizards",
            "description": "Oh yeah."
        }

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSessionMixin,
            CreateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceCreateView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse("vocab_admin:vocab_source_create")
        )
        self.assertEqual(found.func.__name__, VocabSourceCreateView.as_view().__name__)

    def test_view_non_authenticated_user_redirected_to_login(self):
        response = self.client.get(
            reverse("vocab_admin:vocab_source_create")
        )
        self.assertRedirects(
            response,
            expected_url="{0}?next=/admin/{1}/source/create/".format(
                reverse(settings.LOGIN_URL),
                URL_PREFIX,
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=""
        )

    def test_view_returns_correct_status_code(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse("vocab_admin:vocab_source_create")
        )
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse("vocab_admin:vocab_source_create")
        )
        self.assertTemplateUsed(response, "{0}/admin/vocab_source_create.html".format(APP_NAME))

    def test_view_uses_correct_form(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse("vocab_admin:vocab_source_create")
        )
        self.assertIsInstance(response.context["form"], VocabSourceCreateForm)

    def test_view_injects_form_kwargs(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse("vocab_admin:vocab_source_create")
        )
        form = response.context["form"]
        self.assertEqual(form.creator, self.user)

    def test_view_creates_object(self):
        self.login_test_user(self.user.username)
        self.assertFalse(
            VocabSource.objects.filter(
                name=self.vocab_source_data["name"],
                source_type=self.vocab_source_data["source_type"]
            ).exists()
        )
        self.client.post(
            reverse("vocab_admin:vocab_source_create"),
            self.vocab_source_data
        )
        self.assertTrue(
            VocabSource.objects.filter(
                name=self.vocab_source_data["name"],
                source_type=self.vocab_source_data["source_type"]
            ).exists()
        )

    def test_invalid_data_shows_form_errors_and_does_not_save(self):
        self.vocab_source_data["name"] = ""
        self.login_test_user(self.user.username)
        response = self.client.post(
            reverse("vocab_admin:vocab_source_create"),
            self.vocab_source_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            VocabSource.objects.filter(
                name=self.vocab_source_data["name"],
                source_type=self.vocab_source_data["source_type"]
            ).exists()
        )
        self.assertIsInstance(response.context["form"], VocabSourceCreateForm)
        self.assertFormError(response, "form", "name", error_messages["field_required"])

    def test_view_redirects_on_success(self):
        self.login_test_user(self.user.username)
        response = self.client.post(
            reverse("vocab_admin:vocab_source_create"),
            self.vocab_source_data
        )
        vocab_source = VocabSource.objects.get(
            name=self.vocab_source_data["name"]
        )
        self.assertRedirects(
            response,
            expected_url=reverse(
                "vocab_admin:vocab_source_dashboard",
                kwargs={"vocab_source_slug": vocab_source.slug}
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=""
        )


class VocabSourceUpdateViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceUpdateViewTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            source_type=VocabSource.BOOK,
            name="A good book"
        )

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSourceMixin,
            UpdateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceUpdateView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                "vocab_admin:vocab_source_update",
                kwargs={"pk": self.vocab_source.id}
            )
        )
        self.assertEqual(found.func.__name__, VocabSourceUpdateView.as_view().__name__)

    def test_view_non_authenticated_user_redirected_to_login(self):
        response = self.client.get(
            reverse(
                "vocab_admin:vocab_source_update",
                kwargs={"pk": self.vocab_source.id}
            )
        )
        self.assertRedirects(
            response,
            expected_url="{0}?next=/admin/{1}/source/{2}/update/".format(
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
                "vocab_admin:vocab_source_update",
                kwargs={"pk": self.vocab_source.id}
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                "vocab_admin:vocab_source_update",
                kwargs={"pk": self.vocab_source.id}
            )
        )
        self.assertTemplateUsed(response, "{0}/admin/vocab_source_update.html".format(APP_NAME))

    def test_view_uses_correct_form(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                "vocab_admin:vocab_source_update",
                kwargs={"pk": self.vocab_source.id}
            )
        )
        self.assertIsInstance(response.context["form"], VocabSourceUpdateForm)


class VocabSourceDeleteViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceDeleteViewTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            source_type=VocabSource.BOOK,
            name="A good book"
        )

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            AjaxDeleteMixin,
            DeleteView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceDeleteView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse(
            "vocab_admin:vocab_source_delete",
            kwargs={"pk": self.vocab_source.id})
        )
        self.assertEqual(found.func.__name__, VocabSourceDeleteView.as_view().__name__)

    def test_view_non_authenticated_user_redirected_to_login(self):
        response = self.client.get(
            reverse("vocab_admin:vocab_source_delete", kwargs={"pk": self.vocab_source.id})
        )
        self.assertRedirects(
            response,
            expected_url="{url}?next=/admin/{module}/source/{pk}/delete/".format(
                url=reverse(settings.LOGIN_URL),
                module=URL_PREFIX,
                pk=self.vocab_source.id
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=""
        )

    def test_view_returns_correct_status_code(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse("vocab_admin:vocab_source_delete", kwargs={"pk": self.vocab_source.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse("vocab_admin:vocab_source_delete", kwargs={"pk": self.vocab_source.id})
        )
        self.assertTemplateUsed(response, "{0}/admin/vocab_source_delete_confirm.html".format(APP_NAME))

    def test_view_deletes_object(self):
        self.login_test_user(self.user.username)
        obj_id = self.vocab_source.id
        self.assertTrue(VocabSource.objects.filter(pk=obj_id).exists())
        self.client.post(
            reverse("vocab_admin:vocab_source_delete", kwargs={"pk": obj_id})
        )
        self.assertFalse(VocabSource.objects.filter(pk=obj_id).exists())

    def test_view_redirects_on_success(self):
        self.login_test_user(self.user.username)
        response = self.client.post(
            reverse("vocab_admin:vocab_source_delete", kwargs={"pk": self.vocab_source.id})
        )
        self.assertRedirects(
            response,
            expected_url=reverse("vocab_admin:user_vocab_sources"),
            status_code=302,
            target_status_code=200,
            msg_prefix=""
        )

    def test_view_ajax(self):
        self.login_test_user(self.user.username)
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        obj_id = self.vocab_source.id
        self.assertTrue(VocabSource.objects.filter(pk=obj_id).exists())
        response = self.client.post(
            reverse("vocab_admin:vocab_source_delete", kwargs={"pk": obj_id}),
            **kwargs
        )
        self.assertEqual(response.status_code, 200)
        json_string = response.content.decode("utf-8")
        response_data = json.loads(json_string)
        self.assertEqual(_("message_success"), response_data["success_message"])
        self.assertFalse(VocabSource.objects.filter(pk=obj_id).exists())


class VocabSourceEntriesViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceEntriesViewTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            source_type=VocabSource.BOOK,
            name="A good book"
        )

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSourceMixin,
            TemplateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceEntriesView, class_name))

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

    def test_num_queries(self):
        self.login_test_user(self.user.username)
        with self.assertNumQueries(FuzzyInt(1, 11)):
            self.client.get(
                reverse(
                    "vocab_admin:vocab_source_entries",
                    kwargs={
                        "vocab_source_pk": self.vocab_source.id,
                        "vocab_source_slug": self.vocab_source.slug
                    }
                )
            )


class VocabSourceContextsViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceContextsViewTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            source_type=VocabSource.BOOK,
            name="A good book"
        )
        self.vocab_entry_1 = VocabEntry.objects.create(creator=self.user, language="es", entry="tergiversar")
        self.vocab_entry_2 = VocabEntry.objects.create(creator=self.user, language="es", entry="demasiado")

    def add_contexts(self):
        context_text = """Hay que tergiversar el mensaje, pero no demasiado. Demasiado sería
                          no solo confuso, sino devastador."""
        for i in range(1, 20):
            vocab_context = VocabContext.objects.create(vocab_source=self.vocab_source, content=context_text)
            vocab_context_entry_1 = VocabContextEntry.objects.create(
                vocab_context=vocab_context,
                vocab_entry=self.vocab_entry_1
            )
            vocab_context_entry_1.add_vocab_entry_tag("demasiado")
            vocab_context_entry_2 = VocabContextEntry.objects.create(
                vocab_context=vocab_context,
                vocab_entry=self.vocab_entry_2
            )
            vocab_context_entry_2.add_vocab_entry_tag("demasiado")

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSourceMixin,
            ListView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceContextsView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse(
            "vocab_admin:vocab_source_contexts",
            kwargs={"vocab_source_pk": self.vocab_source.id})
        )
        self.assertEqual(found.func.__name__, VocabSourceContextsView.as_view().__name__)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                "vocab_admin:vocab_source_contexts",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            )
        )
        self.assertTemplateUsed(response, "{0}/admin/vocab_source_contexts.html".format(APP_NAME))

    def test_num_queries(self):
        self.login_test_user(self.user.username)
        self.add_contexts()
        with self.assertNumQueries(FuzzyInt(1, 11)):
            self.client.get(
                reverse(
                    "vocab_admin:vocab_source_contexts",
                    kwargs={"vocab_source_pk": self.vocab_source.id}
                )
            )


class VocabSourceContextEntriesViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceContextEntriesViewTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            source_type=VocabSource.BOOK,
            name="A good book"
        )
        self.vocab_entry_1 = VocabEntry.objects.create(creator=self.user, language="es", entry="tergiversar")
        self.vocab_entry_2 = VocabEntry.objects.create(creator=self.user, language="es", entry="demasiado")

    def add_contexts(self):
        context_text = """Hay que tergiversar el mensaje, pero no demasiado. Demasiado sería
                          no solo confuso, sino devastador."""
        for i in range(1, 20):
            vocab_context = VocabContext.objects.create(
                vocab_source=self.vocab_source,
                content=context_text
            )
            vocab_context_entry_1 = VocabContextEntry.objects.create(
                vocab_context=vocab_context,
                vocab_entry=self.vocab_entry_1
            )
            vocab_context_entry_1.add_vocab_entry_tag("demasiado")
            vocab_context_entry_2 = VocabContextEntry.objects.create(
                vocab_context=vocab_context,
                vocab_entry=self.vocab_entry_2
            )
            vocab_context_entry_2.add_vocab_entry_tag("demasiado")

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSourceMixin,
            ListView
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(VocabSourceContextEntriesView, class_name)
            )

    def test_correct_view_used(self):
        found = resolve(reverse(
            "vocab_admin:vocab_source_context_entries",
            kwargs={
                "vocab_source_pk": self.vocab_source.id,
                "language": self.vocab_entry_1.language,
                "vocab_entry_slug": self.vocab_entry_1.slug
            })
        )
        self.assertEqual(
            found.func.__name__, VocabSourceContextEntriesView.as_view().__name__
        )

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                "vocab_admin:vocab_source_context_entries",
                kwargs={
                    "vocab_source_pk": self.vocab_source.id,
                    "language": self.vocab_entry_1.language,
                    "vocab_entry_slug": self.vocab_entry_1.slug
                }
            )
        )
        self.assertTemplateUsed(
            response,
            "{0}/admin/vocab_source_context_entries.html".format(APP_NAME)
        )

    def test_num_queries(self):
        self.login_test_user(self.user.username)
        self.add_contexts()
        with self.assertNumQueries(FuzzyInt(1, 11)):
            self.client.get(
                reverse(
                    "vocab_admin:vocab_source_context_entries",
                    kwargs={
                        "vocab_source_pk": self.vocab_source.id,
                        "language": self.vocab_entry_1.language,
                        "vocab_entry_slug": self.vocab_entry_1.slug
                    }
                )
            )


class ExportVocabSourceJsonViewTest(TestCommon):

    def test_export_source_json_to_file(self):
        pass
