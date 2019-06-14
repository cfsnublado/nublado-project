import json

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import resolve, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView, DeleteView,
    UpdateView, View
)

from core.views import (
    AjaxDeleteMixin, JsonAttachmentMixin,
    MessageMixin
)
from ..conf import settings
from ..forms import VocabSourceCreateForm, VocabSourceUpdateForm
from ..models import (
    VocabEntry, VocabContext, VocabContextEntry,
    VocabProject, VocabSource
)
from ..utils import export_vocab_source
from ..views.views_mixins import (
    VocabProjectMixin,
    VocabSourceMixin, VocabSourcePermissionMixin,
    VocabSourceSessionMixin
)
from ..views.views_vocab_source_auth import (
    VocabSourceCreateView, VocabSourceDeleteView,
    VocabSourceExportJsonView, VocabSourceUpdateView
)

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
            name='test source'
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)

    def add_session_to_request(self, request):
        '''Annotate a request object with a session'''
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()


class VocabSourceCreateViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceCreateViewTest, self).setUp()
        self.vocab_source_data = {
            'source_type': VocabSource.BOOK,
            'name': 'A tale of two wizards',
            'description': 'Oh yeah.'
        }

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabProjectMixin,
            MessageMixin,
            CreateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceCreateView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )
        self.assertEqual(found.func.__name__, VocabSourceCreateView.as_view().__name__)

    def test_view_non_authenticated_user_redirected_to_login(self):
        response = self.client.get(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )
        self.assertRedirects(
            response,
            expected_url='{0}?next=/{1}/auth/project/{2}-{3}/source/create/'.format(
                reverse(settings.LOGIN_URL),
                URL_PREFIX,
                self.vocab_project.id,
                self.vocab_project.slug
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_view_returns_correct_status_code(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )
        self.assertTemplateUsed(response, '{0}/auth/vocab_source_create.html'.format(APP_NAME))

    def test_view_uses_correct_form(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )
        self.assertIsInstance(response.context['form'], VocabSourceCreateForm)

    def test_view_injects_form_kwargs(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            )
        )
        form = response.context['form']
        self.assertEqual(form.creator, self.user)
        self.assertEqual(form.vocab_project, self.vocab_project)

    def test_view_creates_object(self):
        self.login_test_user(self.user.username)
        self.assertFalse(
            VocabSource.objects.filter(
                vocab_project=self.vocab_project,
                creator=self.user,
                name=self.vocab_source_data['name'],
                source_type=self.vocab_source_data['source_type']
            ).exists()
        )
        self.client.post(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            ),
            self.vocab_source_data
        )
        self.assertTrue(
            VocabSource.objects.filter(
                vocab_project=self.vocab_project,
                creator=self.user,
                name=self.vocab_source_data['name'],
                source_type=self.vocab_source_data['source_type']
            ).exists()
        )

    def test_invalid_data_shows_form_errors_and_does_not_save(self):
        self.vocab_source_data['name'] = ''
        self.login_test_user(self.user.username)
        response = self.client.post(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            ),
            self.vocab_source_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            VocabSource.objects.filter(
                name=self.vocab_source_data['name'],
                source_type=self.vocab_source_data['source_type']
            ).exists()
        )
        self.assertIsInstance(response.context['form'], VocabSourceCreateForm)
        self.assertFormError(response, 'form', 'name', _('validation_field_required'))

    def test_view_redirects_on_success(self):
        self.login_test_user(self.user.username)
        response = self.client.post(
            reverse(
                'vocab:vocab_source_create',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            ),
            self.vocab_source_data
        )
        vocab_source = VocabSource.objects.get(
            name=self.vocab_source_data['name']
        )
        self.assertRedirects(
            response,
            expected_url=reverse(
                'vocab:vocab_source_dashboard',
                kwargs={
                    'vocab_source_pk': vocab_source.id,
                    'vocab_source_slug': vocab_source.slug
                }
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )


class VocabSourceUpdateViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceUpdateViewTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            vocab_project=self.vocab_project,
            source_type=VocabSource.BOOK,
            name='A good book'
        )

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSourceMixin,
            VocabSourceSessionMixin,
            VocabSourcePermissionMixin,
            MessageMixin,
            UpdateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceUpdateView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                'vocab:vocab_source_update',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        self.assertEqual(found.func.__name__, VocabSourceUpdateView.as_view().__name__)

    def test_view_non_authenticated_user_redirected_to_login(self):
        response = self.client.get(
            reverse(
                'vocab:vocab_source_update',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        self.assertRedirects(
            response,
            expected_url='{0}?next=/{1}/auth/source/{2}-{3}/update/'.format(
                reverse(settings.LOGIN_URL),
                URL_PREFIX,
                self.vocab_source.id,
                self.vocab_source.slug
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_view_returns_correct_status_code(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_update',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_update',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        self.assertTemplateUsed(response, '{0}/auth/vocab_source_update.html'.format(APP_NAME))

    def test_view_uses_correct_form(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_update',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id,
                    'vocab_source_slug': self.vocab_source.slug
                }
            )
        )
        self.assertIsInstance(response.context['form'], VocabSourceUpdateForm)


class VocabSourceDeleteViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceDeleteViewTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            vocab_project=self.vocab_project,
            source_type=VocabSource.BOOK,
            name='A good book'
        )

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSourceMixin,
            VocabSourceSessionMixin,
            VocabSourcePermissionMixin,
            AjaxDeleteMixin,
            DeleteView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceDeleteView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                'vocab:vocab_source_delete',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id
                }
            )
        )
        self.assertEqual(found.func.__name__, VocabSourceDeleteView.as_view().__name__)

    def test_view_non_authenticated_user_redirected_to_login(self):
        response = self.client.get(
            reverse(
                'vocab:vocab_source_delete',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id
                }
            )
        )
        self.assertRedirects(
            response,
            expected_url='{0}?next=/{1}/auth/source/{2}/delete/'.format(
                reverse(settings.LOGIN_URL),
                URL_PREFIX,
                self.vocab_source.id
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_view_returns_correct_status_code(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_delete',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id
                }
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_source_delete',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id
                }
            )
        )
        self.assertTemplateUsed(response, '{0}/auth/vocab_source_delete_confirm.html'.format(APP_NAME))

    def test_view_deletes_object(self):
        self.login_test_user(self.user.username)
        obj_id = self.vocab_source.id
        self.assertTrue(VocabSource.objects.filter(pk=obj_id).exists())
        self.client.post(
            reverse(
                'vocab:vocab_source_delete',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id
                }
            )
        )
        self.assertFalse(VocabSource.objects.filter(pk=obj_id).exists())

    def test_view_redirects_on_success(self):
        self.login_test_user(self.user.username)
        response = self.client.post(
            reverse(
                'vocab:vocab_source_delete',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id
                }
            )
        )
        self.assertRedirects(
            response,
            expected_url=reverse(
                'vocab:vocab_project_dashboard',
                kwargs={
                    'vocab_project_pk': self.vocab_project.id,
                    'vocab_project_slug': self.vocab_project.slug
                }
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_view_ajax(self):
        self.login_test_user(self.user.username)
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        obj_id = self.vocab_source.id
        self.assertTrue(VocabSource.objects.filter(pk=obj_id).exists())
        response = self.client.post(
            reverse(
                'vocab:vocab_source_delete',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id
                }
            ),
            **kwargs
        )
        self.assertEqual(response.status_code, 200)
        json_string = response.content.decode('utf-8')
        response_data = json.loads(json_string)
        self.assertEqual(_('message_success'), response_data['success_message'])
        self.assertFalse(VocabSource.objects.filter(pk=obj_id).exists())


class VocabSourceExportJsonViewTest(TestCommon):

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabSourceMixin,
            VocabSourceSessionMixin,
            VocabSourcePermissionMixin,
            JsonAttachmentMixin,
            View
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceExportJsonView, class_name))

    def test_export_source_json_to_file(self):
        self.login_test_user(self.user.username)
        request = self.request_factory.get('/fake-path')

        vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='This is a sample sentence.'
        )
        vocab_entry = VocabEntry.objects.create(
            entry='sentence',
            language='en'
        )
        VocabContextEntry.objects.create(
            vocab_context=vocab_context,
            vocab_entry=vocab_entry
        )
        response = self.client.get(
            reverse(
                'vocab:vocab_source_export_json',
                kwargs={
                    'vocab_source_pk': self.vocab_source.id
                }
            )
        )
        expected_data = export_vocab_source(request, self.vocab_source)
        self.assertEqual(json.loads(response.content), expected_data)
