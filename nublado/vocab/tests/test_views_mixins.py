from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase
from django.views.generic import DetailView

from core.utils import setup_test_view
from core.views import CachedObjectMixin
from ..models import VocabSource
from ..views.views_mixins import (
    VocabSourceMixin, VocabSourcePermissionMixin,
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


class VocabSourceMixinTest(TestCommon):

    class VocabSourceView(VocabSourceMixin, DetailView):
        model = VocabSource
        template_name = "fake_template.html"

        def get_queryset(self, **kwargs):
            qs = VocabSource.objects.filter(id=self.kwargs["pk"])
            return qs

    def setUp(self):
        super(VocabSourceMixinTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="Test Source"
        )

    def test_inheritance(self):
        classes = (
            CachedObjectMixin,
            VocabSourceSessionMixin,
            VocabSourcePermissionMixin
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
            pk=self.vocab_source.pk
        )
        view.dispatch(view.request, *view.args, **view.kwargs)
        context = view.get_context_data()
        self.assertEqual(context["vocab_source"], self.vocab_source)

    def test_permissions_creator(self):
        request = self.request_factory.get("/fake-path")
        self.add_session_to_request(request)
        request.user = self.user
        view = setup_test_view(self.VocabSourceView(), request, pk=self.vocab_source.pk)
        response = view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertEqual(response.status_code, 200)
        context = view.get_context_data()
        self.assertTrue(context["is_vocab_source_creator"])

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
