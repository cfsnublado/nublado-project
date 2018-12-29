import json

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.test import RequestFactory, TestCase
from django.views.generic import (
    CreateView, DetailView, TemplateView,
    View, UpdateView
)

from coretest.models import TestModel, TestUserstampModel
from ..forms import BaseModelForm
from ..utils import setup_test_view
from ..views import (
    AttachmentMixin, AutocompleteMixin, ObjectSessionMixin,
    SuperuserRequiredMixin, UserMixin, UserRequiredMixin,
    UserstampMixin
)

User = get_user_model()


class TestUserstampForm(BaseModelForm):

    class Meta:
        model = TestUserstampModel
        fields = ['name']


class ObjectSessionMixinTest(TestCase):

    class ObjectSessionView(ObjectSessionMixin, View):
        pass

    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(
            username='foo7',
            first_name='Foo',
            last_name='Foo',
            email='foo7@foo.com',
            password='Coffee?69c'
        )
        self.test_model = TestModel.objects.create(name='hello')
        self.test_model_2 = TestModel.objects.create(name='goodbye')
        self.request_factory = RequestFactory()

    def add_session_to_request(self, request):
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

    def test_view_set_session_obj(self):
        request = self.request_factory.get('/fake-path')
        request.user = self.user
        self.add_session_to_request(request)

        # Session object is self.test_model
        view = setup_test_view(self.ObjectSessionView(), request)
        view.test_model = self.test_model
        view.session_obj = 'test_model'
        view.session_obj_attrs = ['name']
        view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertIn('session_obj', request.session)
        self.assertEqual(
            request.session['session_obj'],
            {view.session_obj: {'name': self.test_model.name}}
        )

        # Session object is self.test_model_2
        view = setup_test_view(self.ObjectSessionView(), request)
        view.test_model = self.test_model_2
        view.session_obj = 'test_model'
        view.session_obj_attrs = ['name']
        view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertIn('session_obj', request.session)
        self.assertEqual(
            request.session['session_obj'],
            {view.session_obj: {'name': self.test_model_2.name}}
        )

        # Session object is None, and request.session['session_obj'] is deleted.
        view = setup_test_view(self.ObjectSessionView(), request)
        view.test_model = self.test_model_2
        view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertNotIn('session_obj', request.session)


class AutocompleteMixinTest(TestCase):

    class AutocompleteView(AutocompleteMixin, View):
        search_model = TestModel
        search_field = 'name'
        search_filter = 'istartswith'
        id_attr = 'id'
        label_attr = 'name'
        value_attr = 'name'

    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(
            username='foo7',
            first_name='Foo',
            last_name='Foo',
            email='foo7@foo.com',
            password='Coffee?69c'
        )
        self.test_model = TestModel.objects.create(name='hello')
        self.request_factory = RequestFactory()

    def get_autocomplete_response(self, term=''):
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        request = self.request_factory.get('/fake-path?term={0}'.format(term), **kwargs)
        response = self.AutocompleteView.as_view()(request)
        return json.loads(response.content)

    def test_autocomplete_results(self):
        result_1 = TestModel.objects.create(name='green')
        result_2 = TestModel.objects.create(name='great')
        result_3 = TestModel.objects.create(name='apple')
        TestModel.objects.create(name='pear')

        results = self.get_autocomplete_response(term='gre')
        expected_results = [
            {'id': result_1.id, 'label': result_1.name, 'value': result_1.name},
            {'id': result_2.id, 'label': result_2.name, 'value': result_2.name}
        ]
        self.assertCountEqual(results, expected_results)

        results = self.get_autocomplete_response(term='gree')
        expected_results = [
            {'id': result_1.id, 'label': result_1.name, 'value': result_1.name}
        ]
        self.assertCountEqual(results, expected_results)

        results = self.get_autocomplete_response(term='ap')
        expected_results = [
            {'id': result_3.id, 'label': result_3.name, 'value': result_3.name}
        ]
        self.assertCountEqual(results, expected_results)

        results = self.get_autocomplete_response(term='xx')
        expected_results = []
        self.assertCountEqual(results, expected_results)


class AttachmentMixinTest(TestCase):

    class AttachmentDetailView(AttachmentMixin, DetailView):
        model = TestUserstampModel
        template_name = 'fake_template.html'

        def get_file_content(self):
            return '### Hello there.'

    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(
            username='ale7',
            first_name='Alejandra',
            last_name='Acosta',
            email='ale7@foo.com',
            password='Coffee?69c'
        )
        self.test_model = TestUserstampModel.objects.create(name='hello')
        self.request_factory = RequestFactory()

    def test_get_filename(self):
        request = self.request_factory.get('/fake-path')
        request.user = self.user
        view = setup_test_view(self.AttachmentDetailView(), request, pk=self.test_model.pk)
        view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertEqual(view.get_filename(), 'document.txt')

    def test_get_content_type(self):
        request = self.request_factory.get('/fake-path')
        request.user = self.user
        view = setup_test_view(self.AttachmentDetailView(), request, pk=self.test_model.pk)
        view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertEqual(view.get_content_type(), 'text/plain')

    def test_get_file_content(self):
        request = self.request_factory.get('/fake-path')
        request.user = self.user
        view = setup_test_view(self.AttachmentDetailView(), request, pk=self.test_model.pk)
        view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertEqual(view.get_file_content(), '### Hello there.')

    def test_make_attachment(self):
        request = self.request_factory.get('/fake-path')
        request.user = self.user
        view = setup_test_view(self.AttachmentDetailView(), request, pk=self.test_model.pk)
        view.dispatch(view.request, *view.args, **view.kwargs)
        view.filename = 'foo.md'
        response = HttpResponse(content_type=view.get_content_type())
        response_attachment = view.make_attachment(response)
        content_disposition = 'attachment; filename=foo.md'
        self.assertEqual(content_disposition, response_attachment['Content-Disposition'])

    def test_write_attachment(self):
        request = self.request_factory.get('/fake-path')
        request.user = self.user
        view = setup_test_view(self.AttachmentDetailView(), request, pk=self.test_model.pk)
        view.dispatch(view.request, *view.args, **view.kwargs)
        view.filename = 'foo.md'
        response = view.write_attachment()
        content_disposition = 'attachment; filename=foo.md'
        self.assertEqual(content_disposition, response['Content-Disposition'])
        self.assertEqual(view.get_file_content().encode('utf-8'), response.content)


class UserstampMixinTest(TestCase):

    class UserstampCreateView(UserstampMixin, CreateView):
        model = TestUserstampModel
        form_class = TestUserstampForm
        template_name = 'fake_template.html'

    class UserstampUpdateView(UserstampMixin, UpdateView):
        model = TestUserstampModel
        form_class = TestUserstampForm
        template_name = 'fake_template.html'

        def get_queryset(self, **kwargs):
            qs = TestUserstampModel.objects.filter(id=self.kwargs['pk'])
            return qs

    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(
            username='ale7',
            first_name='Alejandra',
            last_name='Acosta',
            email='ale7@foo.com',
            password='Coffee?69c'
        )
        self.test_model = TestUserstampModel.objects.create(name='hello')
        self.request_factory = RequestFactory()

    def test_create_view_set_created_by_and_last_updated_by(self):
        request = self.request_factory.post('/fake-path', {'name': 'foofoo'})
        request.user = self.user
        view = setup_test_view(self.UserstampCreateView(), request)
        view.dispatch(view.request, *view.args, **view.kwargs)
        model = TestUserstampModel.objects.get(name='foofoo')
        self.assertEqual(model.created_by, self.user)
        self.assertEqual(model.last_updated_by, self.user)

    def test_update_view_set_last_updated_by(self):
        request = self.request_factory.post('/fake-path', {'name': 'foofoo'})
        request.user = self.user
        view = setup_test_view(self.UserstampUpdateView(), request, pk=self.test_model.pk)
        view.dispatch(view.request, *view.args, **view.kwargs)
        self.test_model.refresh_from_db()
        self.assertIsNone(self.test_model.created_by)
        self.assertEqual(self.test_model.last_updated_by, self.user)


class UserMixinTest(TestCase):

    class TestView(UserMixin, TemplateView):
        template_name = 'fake_template.html'

    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(
            username='ale7',
            first_name='Alejandra',
            last_name='Acosta',
            email='ale7@foo.com',
            password='Coffee?69c'
        )
        self.user_2 = User.objects.create_user(
            username='kfl7',
            first_name='Karen',
            last_name='Fuentes',
            email='kfl7@foo.com',
            password='Coffee?69c'
        )

    def add_session_to_request(self, request):
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

    def test_permissions_requesting_existing_user(self):
        request = self.request_factory.get('/fake-path')
        self.add_session_to_request(request)
        request.user = self.user
        view = setup_test_view(self.TestView(), request, username=self.user.username)
        response = view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertEqual(response.status_code, 200)

    def test_permissions_requesting_non_existing_user(self):
        request = self.request_factory.get('/fake-path')
        self.add_session_to_request(request)
        request.user = self.user
        view = setup_test_view(self.TestView(), request, username='nonuser')
        with self.assertRaises(Http404):
            view.dispatch(view.request, *view.args, **view.kwargs)

    def test_view_context_data(self):
        request = self.request_factory.get('/fake-path')
        self.add_session_to_request(request)
        request.user = self.user
        view = setup_test_view(self.TestView(), request, username=self.user_2.username)
        view.dispatch(view.request, *view.args, **view.kwargs)
        context = view.get_context_data()
        self.assertEqual(context['requested_user'], self.user_2)


class SuperuserRequiredMixinTest(TestCase):

    class TestView(SuperuserRequiredMixin, UserstampMixin, CreateView):
        model = TestUserstampModel
        form_class = TestUserstampForm
        template_name = 'fake_template.html'

    def setUp(self):
        self.request_factory = RequestFactory()
        self.superuser = User.objects.create_superuser(
            username='cfs',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs@nublado.foo',
            password='Coffee?69c'
        )
        self.user = User.objects.create_user(
            username='ale7',
            first_name='Alejandra',
            last_name='Acosta',
            email='ale7@foo.com',
            password='Coffee?69c'
        )
        self.test_model = TestUserstampModel.objects.create(name='hello')

    def add_session_to_request(self, request):
        '''Annotate a request object with a session'''
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

    def test_permissions_superuser(self):
        request = self.request_factory.get('/fake-path')
        self.add_session_to_request(request)
        request.user = self.superuser
        view = setup_test_view(self.TestView(), request)
        response = view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertEqual(response.status_code, 200)

    def test_permissions_non_superuser(self):
        request = self.request_factory.get('/fake-path')
        self.add_session_to_request(request)
        request.user = self.user
        view = setup_test_view(self.TestView(), request)
        with self.assertRaises(PermissionDenied):
            view.dispatch(view.request, *view.args, **view.kwargs)


class UserRequiredMixinTest(TestCase):

    class TestView(UserRequiredMixin, TemplateView):
        template_name = 'fake_template.html'

    def setUp(self):
        self.request_factory = RequestFactory()
        self.superuser = User.objects.create_superuser(
            username='cfs',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs@nublado.foo',
            password='Coffee?69c'
        )
        self.user = User.objects.create_user(
            username='ale7',
            first_name='Alejandra',
            last_name='Acosta',
            email='ale7@foo.com',
            password='Coffee?69c'
        )
        self.user_2 = User.objects.create_user(
            username='kfl7',
            first_name='Karen',
            last_name='Fuentes',
            email='kfl7@foo.com',
            password='Coffee?69c'
        )

    def add_session_to_request(self, request):
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

    def test_permissions_superuser(self):
        request = self.request_factory.get('/fake-path')
        self.add_session_to_request(request)
        request.user = self.superuser
        view = setup_test_view(self.TestView(), request, username=self.user.username)
        response = view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertEqual(response.status_code, 200)

    def test_permissions_requesting_user_is_requested_user(self):
        request = self.request_factory.get('/fake-path')
        self.add_session_to_request(request)
        request.user = self.user
        view = setup_test_view(self.TestView(), request, username=self.user.username)
        response = view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertEqual(response.status_code, 200)

    def test_permissions_requesting_user_not_requested_user(self):
        request = self.request_factory.get('/fake-path')
        self.add_session_to_request(request)
        request.user = self.user_2
        view = setup_test_view(self.TestView(), request, username=self.user.username)
        with self.assertRaises(PermissionDenied):
            view.dispatch(view.request, *view.args, **view.kwargs)
