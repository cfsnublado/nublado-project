from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.views.generic import TemplateView

from core.utils import setup_test_view
from core.views import CachedObjectMixin, ObjectSessionMixin
from ..models import VocabEntry, VocabSource
from ..views.views_mixins import (
    PermissionMixin, VocabEntryMixin, VocabEntryPermissionMixin, VocabEntrySearchMixin,
    VocabEntrySessionMixin,
    VocabSourceMixin, VocabSourcePermissionMixin, VocabSourceSearchMixin,
    VocabSourceSessionMixin
)

User = get_user_model()


class TestCommon(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.pwd = "Pizza?69p"
        self.user = User.objects.create_user(
            username="cfs",
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


class VocabSourceSessionMixinTest(TestCommon):

    class VocabSourceView(VocabSourceSessionMixin, TemplateView):
        template_name = "fake_template.html"

        def dispatch(self, request, *args, **kwargs):
            self.vocab_source = VocabSource.objects.get(id=self.kwargs["pk"])

            return super(VocabSourceSessionMixin, self).dispatch(request, *args, **kwargs)

    def setUp(self):
        super(VocabSourceSessionMixinTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="Test Source"
        )

    def test_inheritance(self):
        classes = (
            ObjectSessionMixin,
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceSessionMixin, class_name))

    def test_session_data(self):
        request = self.request_factory.get("/fake-path")
        self.add_session_to_request(request)
        request.user = self.user
        view = setup_test_view(
            self.VocabSourceView(),
            request,
            pk=self.vocab_source.pk
        )
        view.dispatch(view.request, *view.args, **view.kwargs)
        view.setup_session(request)
        self.assertEqual(
            request.session["session_obj"],
            {
                "vocab_source": {
                    "id": self.vocab_source.id,
                    "name": self.vocab_source.name,
                    "slug": self.vocab_source.slug
                }
            }
        )


class VocabSourceMixinTest(TestCommon):

    class VocabSourceView(VocabSourceMixin, TemplateView):
        template_name = "fake_template.html"

    def setUp(self):
        super(VocabSourceMixinTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="Test Source"
        )

    def test_inheritance(self):
        classes = (
            CachedObjectMixin,
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceMixin, class_name))

    def test_get_context_data(self):
        request = self.request_factory.get("/fake-path")
        self.add_session_to_request(request)
        request.user = self.user
        view = setup_test_view(
            self.VocabSourceView(),
            request,
            vocab_source_pk=self.vocab_source.pk
        )
        view.dispatch(view.request, *view.args, **view.kwargs)
        context = view.get_context_data()
        self.assertEqual(context["vocab_source"], self.vocab_source)


class VocabSourcePermissionMixinTest(TestCommon):

    class VocabSourceView(VocabSourcePermissionMixin, TemplateView):
        template_name = "fake_template.html"

        def dispatch(self, request, *args, **kwargs):
            self.vocab_source = VocabSource.objects.get(id=self.kwargs["pk"])

            return super(VocabSourcePermissionMixin, self).dispatch(request, *args, **kwargs)

    def setUp(self):
        super(VocabSourcePermissionMixinTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="Test Source"
        )

    def test_inheritance(self):
        classes = (
            PermissionMixin,
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourcePermissionMixin, class_name))

    def test_permissions_creator(self):
        request = self.request_factory.get("/fake-path")
        self.add_session_to_request(request)
        request.user = self.user
        view = setup_test_view(self.VocabSourceView(), request, pk=self.vocab_source.pk)
        response = view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertEqual(response.status_code, 200)

    def test_permissions_not_creator(self):
        user = User.objects.create_user(
            username="non",
            first_name="Non",
            last_name="Member",
            email="nonmember@no.com",
            password=self.pwd
        )
        request = self.request_factory.get("/fake-path")
        self.add_session_to_request(request)
        request.user = user
        view = setup_test_view(self.VocabSourceView(), request, pk=self.vocab_source.pk)
        with self.assertRaises(PermissionDenied):
            view.dispatch(view.request, *view.args, **view.kwargs)


class VocabSourceSearchMixinTest(TestCommon):

    class VocabSourceSearchView(VocabSourceSearchMixin, TemplateView):
        template_name = "fake_template.html"

    def setUp(self):
        super(VocabSourceSearchMixinTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="Test Source"
        )

    def dispatch_view(self, source=None):
        request = self.request_factory.get(
            "/fake-path?source={0}".format(source)
        )
        request.user = self.user
        view = setup_test_view(
            self.VocabSourceSearchView(),
            request
        )
        view.dispatch(view.request, *view.args, **view.kwargs)
        return view

    def get_response(self, source=None):
        request = self.request_factory.get(
            "/fake-path?source={0}".format(source)
        )
        request.user = self.user
        response = self.VocabSourceSearchView.as_view()(request)
        response.client = Client()
        return response

    def test_default_success(self):
        response = self.get_response(
            source=self.vocab_source
        )
        self.assertRedirects(
            response,
            expected_url=reverse(
                "vocab:vocab_source_dashboard",
                kwargs={
                    "vocab_source_slug": self.vocab_source.slug
                }
            ),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=False
        )

    def test_get_context_data(self):
        search_source = "foo"
        view = self.dispatch_view(source=search_source)
        context = view.get_context_data()
        self.assertEqual(context["search_term"], search_source)
        self.assertIsNone(context["vocab_source"])


class VocabEntrySessionMixinTest(TestCommon):

    class VocabEntryView(VocabEntrySessionMixin, TemplateView):
        template_name = "fake_template.html"

        def dispatch(self, request, *args, **kwargs):
            self.vocab_entry = VocabEntry.objects.get(id=self.kwargs["pk"])

            return super(VocabEntrySessionMixin, self).dispatch(request, *args, **kwargs)

    def setUp(self):
        super(VocabEntrySessionMixinTest, self).setUp()
        self.superuser = User.objects.create_superuser(
            username="foo",
            first_name="Christopher",
            last_name="Sanders",
            email="foo7@foo.com",
            password=self.pwd
        )
        self.vocab_entry = VocabEntry.objects.create(
            language="en",
            entry="perplexed"
        )

    def test_inheritance(self):
        classes = (
            ObjectSessionMixin,
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntrySessionMixin, class_name))

    def test_session_data(self):
        request = self.request_factory.get("/fake-path")
        self.add_session_to_request(request)
        request.user = self.user
        view = setup_test_view(
            self.VocabEntryView(),
            request,
            pk=self.vocab_entry.pk
        )
        view.dispatch(view.request, *view.args, **view.kwargs)
        view.setup_session(request)
        self.assertEqual(
            request.session["session_obj"],
            {
                "vocab_entry": {
                    "id": self.vocab_entry.id,
                    "language": self.vocab_entry.language,
                    "entry": self.vocab_entry.entry,
                    "slug": self.vocab_entry.slug
                }
            }
        )


class VocabEntryMixinTest(TestCommon):

    class VocabEntryView(VocabEntryMixin, TemplateView):
        template_name = "fake_template.html"

    def setUp(self):
        super(VocabEntryMixinTest, self).setUp()
        self.superuser = User.objects.create_superuser(
            username="foo",
            first_name="Christopher",
            last_name="Sanders",
            email="foo7@foo.com",
            password=self.pwd
        )
        self.vocab_entry = VocabEntry.objects.create(
            language="en",
            entry="perplexed"
        )

    def test_inheritance(self):
        classes = (
            CachedObjectMixin,
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntryMixin, class_name))

    def test_get_context_data(self):
        request = self.request_factory.get("/fake-path")
        self.add_session_to_request(request)
        request.user = self.user
        view = setup_test_view(
            self.VocabEntryView(),
            request,
            vocab_entry_pk=self.vocab_entry.pk
        )
        view.dispatch(view.request, *view.args, **view.kwargs)
        context = view.get_context_data()
        self.assertEqual(context["vocab_entry"], self.vocab_entry)


class VocabEntryPermissionMixinTest(TestCommon):

    class VocabEntryView(VocabEntryPermissionMixin, TemplateView):
        template_name = "fake_template.html"

        def dispatch(self, request, *args, **kwargs):
            self.vocab_entry = VocabEntry.objects.get(id=self.kwargs["pk"])

            return super(VocabEntryPermissionMixin, self).dispatch(request, *args, **kwargs)

    def setUp(self):
        super(VocabEntryPermissionMixinTest, self).setUp()
        self.superuser = User.objects.create_superuser(
            username="foo",
            first_name="Christopher",
            last_name="Sanders",
            email="foo7@foo.com",
            password=self.pwd
        )
        self.vocab_entry = VocabEntry.objects.create(
            language="en",
            entry="perplexed"
        )

    def test_inheritance(self):
        classes = (
            PermissionMixin,
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntryPermissionMixin, class_name))

    def test_permissions_superuser(self):
        request = self.request_factory.get("/fake-path")
        self.add_session_to_request(request)
        request.user = self.superuser
        view = setup_test_view(self.VocabEntryView(), request, pk=self.vocab_entry.pk)
        response = view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertEqual(response.status_code, 200)

    def test_permissions_not_superuser(self):
        request = self.request_factory.get("/fake-path")
        self.add_session_to_request(request)
        request.user = self.user
        view = setup_test_view(self.VocabEntryView(), request, pk=self.vocab_entry.pk)
        with self.assertRaises(PermissionDenied):
            view.dispatch(view.request, *view.args, **view.kwargs)


class VocabEntrySearchMixinTest(TestCommon):

    class VocabEntrySearchView(VocabEntrySearchMixin, TemplateView):
        template_name = "fake_template.html"

    def setUp(self):
        super(VocabEntrySearchMixinTest, self).setUp()
        self.vocab_entry = VocabEntry.objects.create(
            language="es",
            entry="tergiversar"
        )

    def dispatch_view(self, language=None, term=None):
        request = self.request_factory.get(
            "/fake-path?search_language={0}&search_entry={1}".format(
                language,
                term
            )
        )
        request.user = self.user
        view = setup_test_view(
            self.VocabEntrySearchView(),
            request
        )
        view.dispatch(view.request, *view.args, **view.kwargs)
        return view

    def get_response(self, language=None, entry=None):
        request = self.request_factory.get(
            "/fake-path?search_language={0}&search_entry={1}".format(
                language,
                entry
            )
        )
        request.user = self.user
        response = self.VocabEntrySearchView.as_view()(request)
        response.client = Client()
        return response

    def test_default_success(self):
        response = self.get_response(
            language=self.vocab_entry.language,
            entry=self.vocab_entry.entry
        )
        self.assertRedirects(
            response,
            expected_url=reverse(
                "vocab:vocab_entry",
                kwargs={
                    "vocab_entry_language": self.vocab_entry.language,
                    "vocab_entry_slug": self.vocab_entry.slug
                }
            ),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=False
        )

    def test_get_context_data(self):
        search_language = "es"
        search_term = "fuafua"
        view = self.dispatch_view(language=search_language, term=search_term)
        context = view.get_context_data()
        self.assertEqual(context["search_language"], search_language)
        self.assertEqual(context["search_term"], search_term)
        self.assertIsNone(context["vocab_entry"])

        # Search language defualts to en if not in languages
        search_language = "fr"
        view = self.dispatch_view(language=search_language, term=search_term)
        context = view.get_context_data()
        self.assertEqual(context["search_language"], "en")
        self.assertEqual(context["search_term"], search_term)
        self.assertIsNone(context["vocab_entry"])
