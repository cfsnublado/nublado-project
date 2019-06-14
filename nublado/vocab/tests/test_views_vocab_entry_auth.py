import json

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import resolve, reverse
from django.test import RequestFactory, TestCase
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView, DeleteView, UpdateView
)

from core.views import (
    AjaxDeleteMixin, AjaxFormMixin, MessageMixin,
    ObjectSessionMixin, UserstampMixin
)
from ..conf import settings
from ..forms import VocabEntryCreateForm, VocabEntryUpdateForm
from ..models import (
    VocabEntry
)
from ..views.views_mixins import (
    VocabEntryMixin, VocabEntryPermissionMixin,
    VocabEntrySessionMixin
)
from ..views.views_vocab_entry_auth import (
    VocabEntryCreateView,
    VocabEntryDeleteView, VocabEntryUpdateView
)

User = get_user_model()

APP_NAME = 'vocab'
URL_PREFIX = getattr(settings, 'VOCAB_URL_PREFIX')


class TestCommon(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_superuser(
            username='cfs7',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@foo.com',
            password=self.pwd
        )
        self.vocab_entry = VocabEntry.objects.create(
            language='en',
            entry='detritus'
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)


class VocabEntryCreateViewTest(TestCommon):

    def setUp(self):
        super(VocabEntryCreateViewTest, self).setUp()
        self.vocab_entry_data = {
            'language': 'es',
            'entry': 'tergiversar'
        }

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            ObjectSessionMixin,
            UserstampMixin,
            CreateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntryCreateView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse('vocab:vocab_entry_create'))
        self.assertEqual(found.func.__name__, VocabEntryCreateView.as_view().__name__)

    def test_view_non_authenticated_user_redirected_to_login(self):
        response = self.client.get(reverse('vocab:vocab_entry_create'))
        self.assertRedirects(
            response,
            expected_url='{0}?next=/{1}/auth/entry/create/'.format(
                reverse(settings.LOGIN_URL),
                URL_PREFIX
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_view_returns_correct_status_code(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse('vocab:vocab_entry_create')
        )
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse('vocab:vocab_entry_create')
        )
        self.assertTemplateUsed(response, '{0}/auth/vocab_entry_create.html'.format(APP_NAME))

    def test_view_uses_correct_form(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse('vocab:vocab_entry_create')
        )
        self.assertIsInstance(response.context['form'], VocabEntryCreateForm)

    def test_view_creates_object(self):
        self.login_test_user(self.user.username)
        self.assertFalse(
            VocabEntry.objects.filter(
                entry=self.vocab_entry_data['entry']
            ).exists()
        )
        self.client.post(
            reverse('vocab:vocab_entry_create'),
            self.vocab_entry_data
        )
        self.assertTrue(
            VocabEntry.objects.filter(
                entry=self.vocab_entry_data['entry']
            ).exists()
        )

    def test_invalid_data_shows_form_errors_and_does_not_save(self):
        self.vocab_entry_data['entry'] = ''
        self.login_test_user(self.user.username)
        response = self.client.post(
            reverse('vocab:vocab_entry_create'),
            self.vocab_entry_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            VocabEntry.objects.filter(
                entry=self.vocab_entry_data['entry']
            ).exists()
        )
        self.assertIsInstance(response.context['form'], VocabEntryCreateForm)
        self.assertFormError(response, 'form', 'entry', _('validation_field_required'))

    def test_view_redirects_on_success(self):
        self.login_test_user(self.user.username)
        response = self.client.post(
            reverse('vocab:vocab_entry_create'),
            self.vocab_entry_data
        )
        vocab_entry = VocabEntry.objects.get(
            entry=self.vocab_entry_data['entry']
        )
        self.assertRedirects(
            response,
            expected_url='/{0}/entry/{1}/{2}/'.format(
                URL_PREFIX,
                vocab_entry.language,
                vocab_entry.slug
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )


class VocabEntryUpdateViewTest(TestCommon):

    def setUp(self):
        super(VocabEntryUpdateViewTest, self).setUp()
        self.vocab_entry = VocabEntry.objects.create(entry='hello')

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            VocabEntryMixin,
            VocabEntryPermissionMixin,
            VocabEntrySessionMixin,
            UserstampMixin,
            MessageMixin,
            UpdateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntryUpdateView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                'vocab:vocab_entry_update',
                kwargs={
                    'vocab_entry_language': self.vocab_entry.language,
                    'vocab_entry_slug': self.vocab_entry.slug
                }
            )
        )
        self.assertEqual(found.func.__name__, VocabEntryUpdateView.as_view().__name__)

    def test_view_returns_correct_status_code(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_entry_update',
                kwargs={
                    'vocab_entry_language': self.vocab_entry.language,
                    'vocab_entry_slug': self.vocab_entry.slug
                }
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_entry_update',
                kwargs={
                    'vocab_entry_language': self.vocab_entry.language,
                    'vocab_entry_slug': self.vocab_entry.slug
                }
            )
        )
        self.assertTemplateUsed(response, '{0}/auth/vocab_entry_update.html'.format(APP_NAME))

    def test_view_uses_correct_form(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'vocab:vocab_entry_update',
                kwargs={
                    'vocab_entry_language': self.vocab_entry.language,
                    'vocab_entry_slug': self.vocab_entry.slug
                }
            )
        )
        self.assertIsInstance(response.context['form'], VocabEntryUpdateForm)


class VocabEntryDeleteViewTest(TestCommon):

    def setUp(self):
        super(VocabEntryDeleteViewTest, self).setUp()
        self.user.is_superuser = True
        self.user.save()
        self.vocab_entry = VocabEntry.objects.create(
            language='en',
            entry='hello'
        )

    def test_inheritance(self):
        class_names = (
            LoginRequiredMixin,
            VocabEntryMixin,
            VocabEntryPermissionMixin,
            VocabEntrySessionMixin,
            AjaxDeleteMixin,
            DeleteView
        )
        for class_name in class_names:
            self.assertTrue(
                issubclass(VocabEntryDeleteView, class_name)
            )

    def test_correct_view_used(self):
        found = resolve(reverse(
            'vocab:vocab_entry_delete',
            kwargs={'vocab_entry_pk': self.vocab_entry.id})
        )
        self.assertEqual(found.func.__name__, VocabEntryDeleteView.as_view().__name__)

    def test_view_non_authenticated_user_redirected_to_login(self):
        response = self.client.get(
            reverse('vocab:vocab_entry_delete', kwargs={'vocab_entry_pk': self.vocab_entry.id})
        )
        self.assertRedirects(
            response,
            expected_url='{0}?next=/{1}/auth/entry/{2}/delete/'.format(
                reverse(settings.LOGIN_URL),
                URL_PREFIX,
                self.vocab_entry.id
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_view_returns_correct_status_code(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse('vocab:vocab_entry_delete', kwargs={'vocab_entry_pk': self.vocab_entry.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse('vocab:vocab_entry_delete', kwargs={'vocab_entry_pk': self.vocab_entry.id})
        )
        self.assertTemplateUsed(response, '{0}/auth/vocab_entry_delete_confirm.html'.format(APP_NAME))

    def test_view_deletes_object(self):
        self.login_test_user(self.user.username)
        obj_id = self.vocab_entry.id
        self.assertTrue(VocabEntry.objects.filter(pk=obj_id).exists())
        self.client.post(
            reverse('vocab:vocab_entry_delete', kwargs={'vocab_entry_pk': obj_id})
        )
        self.assertFalse(VocabEntry.objects.filter(pk=obj_id).exists())

    def test_view_redirects_on_success(self):
        self.login_test_user(self.user.username)
        response = self.client.post(
            reverse('vocab:vocab_entry_delete', kwargs={'vocab_entry_pk': self.vocab_entry.id})
        )
        self.assertRedirects(
            response,
            expected_url=reverse('vocab:vocab_entries'),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_view_ajax(self):
        self.login_test_user(self.user.username)
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        obj_id = self.vocab_entry.id
        self.assertTrue(VocabEntry.objects.filter(pk=obj_id).exists())
        response = self.client.post(
            reverse('vocab:vocab_entry_delete', kwargs={'vocab_entry_pk': obj_id}),
            **kwargs
        )
        self.assertEqual(response.status_code, 200)
        json_string = response.content.decode('utf-8')
        response_data = json.loads(json_string)
        self.assertEqual(_('message_success'), response_data['success_message'])
        self.assertFalse(VocabEntry.objects.filter(pk=obj_id).exists())
