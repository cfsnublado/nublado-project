from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import resolve, reverse
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView

from core.views import (
    ObjectSessionMixin,
    UserRequiredMixin
)
from ..conf import settings
from ..forms import (
    UserForgotPasswordRequestForm,
    UserForgotPasswordResetForm, UserPasswordResetForm
)
from ..views import (
    ProfileDetailView, UserForgotPasswordRequestView,
    UserForgotPasswordResetView
)
from ..views_auth import (
    UserPasswordResetView
)

User = get_user_model()

MODULE_NAME = 'users'
URL_PREFIX = 'profile'


class TestCommon(TestCase):

    def setUp(self):
        self.pwd = 'Coffee?69c'
        self.user_data = {
            'username': 'cfs',
            'email': 'ChristopherSanders78@gmail.com.com',
            'first_name': 'cham',
            'last_name': 'cham',
            'password1': self.pwd,
            'password2': self.pwd
        }

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)


class UserForgotPasswordRequestViewTest(TestCommon):

    def setUp(self):
        super(UserForgotPasswordRequestViewTest, self).setUp()
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            password=self.pwd,
        )
        self.form_data = {
            'email': self.user_data['email']
        }

    def test_correct_view_used(self):
        found = resolve(reverse('users:user_password_reset_request'))
        self.assertEqual(found.func.__name__, UserForgotPasswordRequestView.as_view().__name__)

    def test_view_renders_correct_template(self):
        response = self.client.get(reverse('users:user_password_reset_request'))
        self.assertTemplateUsed(response, '{0}/password_reset_request.html'.format(MODULE_NAME))

    def test_view_redirects_if_user_authenticated(self):
        self.login_test_user(username=self.user.username)
        response = self.client.get(reverse('users:user_password_reset_request'))
        self.assertRedirects(
            response,
            expected_url=reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_view_email_templates(self):
        response = self.client.post(reverse('users:user_password_reset_request'), self.form_data)
        self.assertTemplateUsed(response, '{0}/password_reset_request_email.html'.format(MODULE_NAME))
        self.assertTemplateUsed(response, '{0}/password_reset_request_subject.txt'.format(MODULE_NAME))

    def test_view_returns_correct_status_code(self):
        response = self.client.get(reverse('users:user_password_reset_request'))
        self.assertEqual(response.status_code, 200)

    def test_view_sends_email(self):
        self.client.post(reverse('users:user_password_reset_request'), self.form_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_data['email'].lower()])

    def test_view_does_not_send_email_with_unregistered_email(self):
        self.form_data['email'] = 'foo@foo.com'
        self.client.post(reverse('users:user_password_reset_request'), self.form_data)
        self.assertEqual(len(mail.outbox), 0)

    def test_view_uses_correct_form(self):
        response = self.client.get(reverse('users:user_password_reset_request'))
        self.assertIsInstance(response.context['form'], UserForgotPasswordRequestForm)

    def test_view_invalid_data_passes_form_to_template(self):
        self.form_data['email'] = ''
        response = self.client.post(reverse('users:user_password_reset_request'), self.form_data)
        self.assertIsInstance(response.context['form'], UserForgotPasswordRequestForm)

    def test_invalid_data(self):
        self.form_data['email'] = ''
        response = self.client.post(reverse('users:user_password_reset_request'), self.form_data)
        self.assertFormError(response, 'form', 'email', _('validation_field_required'))


class UserPasswordResetViewTest(TestCommon):

    def setUp(self):
        super(UserPasswordResetViewTest, self).setUp()
        self.changed_pwd = 'Pizza?69cc'
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            password=self.pwd,
        )
        self.form_data = {
            'current_password': self.pwd,
            'password1': self.changed_pwd,
            'password2': self.changed_pwd
        }

    def test_inheritance(self):
        classes = (
            LoginRequiredMixin,
            UserRequiredMixin,
            ObjectSessionMixin,
            UpdateView
        )
        for class_name in classes:
            self.assertTrue(issubclass(UserPasswordResetView, class_name))

    def test_correct_view_used(self):
        self.login_test_user(self.user.username)
        found = resolve(reverse('users:user_password_reset', kwargs={'username': self.user.username}))
        self.assertEqual(found.func.__name__, UserPasswordResetView.as_view().__name__)

    def test_view_renders_correct_template(self):
        self.login_test_user(self.user.username)
        response = self.client.get(reverse('users:user_password_reset', kwargs={'username': self.user.username}))
        self.assertTemplateUsed(response, '{0}/auth/password_reset.html'.format(MODULE_NAME))

    def test_view_returns_correct_status_code(self):
        self.login_test_user(self.user.username)
        response = self.client.get(reverse('users:user_password_reset', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_form(self):
        self.login_test_user(self.user.username)
        response = self.client.get(reverse('users:user_password_reset', kwargs={'username': self.user.username}))
        self.assertIsInstance(response.context['form'], UserPasswordResetForm)

    def test_view_redirects_if_user_not_authenticated(self):
        response = self.client.get(reverse('users:user_password_reset', kwargs={'username': self.user.username}))
        self.assertRedirects(
            response,
            expected_url='{0}?next=/{1}/update/{2}/password-reset/'.format(
                reverse(settings.LOGIN_URL),
                URL_PREFIX,
                self.user.username
            ),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_view_user_permissions(self):
        user2 = User.objects.create_user(
            username='kfl',
            email='kfl@kfl.com',
            first_name='Karen',
            last_name='Fuentes',
            password=self.pwd,
        )
        # owner of profile
        self.login_test_user(self.user.username)
        response = self.client.get(reverse('users:user_password_reset', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        # authenticated user other than same profile user
        self.login_test_user(user2.username)
        response = self.client.get(reverse('users:user_password_reset', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 403)
        self.client.logout()
        # superuser
        user2.is_superuser = True
        user2.save()
        self.login_test_user(user2.username)
        response = self.client.get(reverse('users:user_password_reset', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_view_changes_password(self):
        self.login_test_user(self.user.username)
        self.client.post(
            reverse('users:user_password_reset', kwargs={'username': self.user.username}),
            self.form_data
        )
        self.user.refresh_from_db()
        self.assertFalse(self.client.login(username=self.user.username, password=self.pwd))
        self.assertTrue(self.client.login(username=self.user.username, password=self.changed_pwd))


class UserForgotPasswordResetViewTest(TestCommon):

    def setUp(self):
        super(UserForgotPasswordResetViewTest, self).setUp()
        self.changed_pwd = 'Pizza?69cc'
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            password=self.user_data['password1'],
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.form_data = {
            'password1': self.changed_pwd,
            'password2': self.changed_pwd
        }

    def test_view_redirects_if_user_authenticated(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'users:user_forgot_password_reset',
                kwargs={'uidb64': self.uid, 'token': self.token}
            )
        )
        self.assertRedirects(
            response,
            expected_url=reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_correct_view_used(self):
        found = resolve(reverse('users:user_forgot_password_reset', kwargs={'uidb64': self.uid, 'token': self.token}))
        self.assertEqual(found.func.__name__, UserForgotPasswordResetView.as_view().__name__)

    def test_view_renders_correct_template(self):
        response = self.client.get(reverse('users:user_forgot_password_reset', kwargs={'uidb64': self.uid, 'token': self.token}))
        self.assertTemplateUsed(response, '{0}/forgot_password_reset.html'.format(MODULE_NAME))

    def test_view_returns_correct_status_code(self):
        response = self.client.get(reverse('users:user_forgot_password_reset', kwargs={'uidb64': self.uid, 'token': self.token}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_form(self):
        response = self.client.get(reverse('users:user_forgot_password_reset', kwargs={'uidb64': self.uid, 'token': self.token}))
        self.assertIsInstance(response.context['form'], UserForgotPasswordResetForm)

    def test_view_changes_password(self):
        self.client.post(
            reverse('users:user_forgot_password_reset', kwargs={'uidb64': self.uid, 'token': self.token}),
            self.form_data
        )
        self.user.refresh_from_db()
        self.assertFalse(self.client.login(username=self.user.username, password=self.pwd))
        self.assertTrue(self.client.login(username=self.user.username, password=self.changed_pwd))

    def test_view_invalid_data_passes_form_to_template(self):
        self.form_data['password1'] = ''
        response = self.client.post(
            reverse('users:user_forgot_password_reset', kwargs={'uidb64': self.uid, 'token': self.token}),
            self.form_data
        )
        self.assertIsInstance(response.context['form'], UserForgotPasswordResetForm)

    def test_invalid_data(self):
        self.form_data['password1'] = ''
        response = self.client.post(
            reverse('users:user_forgot_password_reset', kwargs={'uidb64': self.uid, 'token': self.token}),
            self.form_data
        )
        self.assertFormError(response, 'form', 'password1', _('validation_field_required'))

    def test_invalid_link_after_password_reset(self):
        response = self.client.get(
            reverse('users:user_forgot_password_reset', kwargs={'uidb64': self.uid, 'token': self.token}),
        )
        self.assertEqual(response.status_code, 200)
        self.client.post(
            reverse('users:user_forgot_password_reset', kwargs={'uidb64': self.uid, 'token': self.token}),
            self.form_data
        )
        # Link is invalid after resetting the password.
        response = self.client.get(
            reverse('users:user_forgot_password_reset', kwargs={'uidb64': self.uid, 'token': self.token}),
        )
        self.assertEqual(response.status_code, 404)


class ProfileDetailViewTest(TestCommon):

    def setUp(self):
        super(ProfileDetailViewTest, self).setUp()
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            password=self.user_data['password1'],
        )

    def test_correct_view_used(self):
        found = resolve(reverse('users:profile_view', kwargs={'username': self.user.username}))
        self.assertEqual(found.func.__name__, ProfileDetailView.as_view().__name__)

    def test_view_renders_correct_template(self):
        response = self.client.get(reverse('users:profile_view', kwargs={'username': self.user.username}))
        self.assertTemplateUsed(response, '{0}/profile_view.html'.format(MODULE_NAME))

    def test_view_returns_correct_status_code(self):
        response = self.client.get(reverse('users:profile_view', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)

    def test_view_is_user(self):
        response = self.client.get(reverse('users:profile_view', kwargs={'username': self.user.username}))
        self.assertFalse(response.context['is_user'])
        self.login_test_user(username=self.user.username)
        response = self.client.get(reverse('users:profile_view', kwargs={'username': self.user.username}))
        self.assertTrue(response.context['is_user'])

    def test_view_context_data(self):
        response = self.client.get(reverse('users:profile_view', kwargs={'username': self.user.username}))
        self.assertEqual(response.context['user_profile'], self.user)
        self.assertEqual(response.context['profile'], self.user.profile)
        self.assertFalse(response.context['is_user'])


# class ProfileUpdateViewTest(TestCommon):

#     def setUp(self):
#         super(ProfileUpdateViewTest, self).setUp()
#         self.profile_data = {
#             'user-email': 'cfs@cfs.com',
#             'user-first_name': 'Foo',
#             'user-last_name': 'Fum',
#             'profile-about': 'Hello. I am fine.'
#         }
#         self.user = User.objects.create_user(
#             username=self.user_data['username'],
#             email=self.user_data['email'],
#             first_name=self.user_data['first_name'],
#             last_name=self.user_data['last_name'],
#             password=self.user_data['password1'],
#         )
#         self.profile = self.user.profile

#     def test_inheritance(self):
#         classes = (
#             LoginRequiredMixin,
#             UserRequiredMixin,
#             CachedObjectMixin,
#             AjaxMultiFormMixin,
#             ObjectSessionMixin,
#             UpdateView
#         )
#         for class_name in classes:
#             self.assertTrue(issubclass(ProfileUpdateView, class_name))

#     def test_view_redirects_to_login_for_unathenticated_user(self):
#         # non authenticated user
#         response = self.client.get(reverse('users:profile_update', kwargs={'username': self.user.username}))
#         self.assertRedirects(
#             response,
#             expected_url='{0}?next=/{1}/update/{2}/'.format(
#                 reverse(settings.LOGIN_URL),
#                 URL_PREFIX,
#                 self.user.username
#             ),
#             status_code=302,
#             target_status_code=200,
#             msg_prefix=''
#         )

#     def test_view_user_permissions(self):
#         user2 = User.objects.create_user(
#             username='kfl',
#             email='kfl@kfl.com',
#             first_name='Karen',
#             last_name='Fuentes',
#             password=self.pwd,
#         )
#         # owner of profile
#         self.login_test_user(self.user.username)
#         response = self.client.get(reverse('users:profile_update', kwargs={'username': self.user.username}))
#         self.assertEqual(response.status_code, 200)
#         self.client.logout()
#         # authenticated user other than same profile user
#         self.login_test_user(user2.username)
#         response = self.client.get(reverse('users:profile_update', kwargs={'username': self.user.username}))
#         self.assertEqual(response.status_code, 403)
#         self.client.logout()
#         # superuser
#         user2.is_superuser = True
#         user2.save()
#         self.login_test_user(user2.username)
#         response = self.client.get(reverse('users:profile_update', kwargs={'username': self.user.username}))
#         self.assertEqual(response.status_code, 200)
#         self.client.logout()

#     def test_correct_view_used(self):
#         self.login_test_user(self.user.username)
#         found = resolve(reverse('users:profile_update', kwargs={'username': self.user.username}))
#         self.assertEqual(found.func.__name__, ProfileUpdateView.as_view().__name__)

#     def test_view_updates_profile(self):
#         self.profile_data['profile-about'] = 'Ooooh yeah'
#         self.login_test_user(self.user.username)
#         self.client.post(
#             reverse('users:profile_update', kwargs={'username': self.user.username}),
#             data=self.profile_data
#         )
#         self.user.refresh_from_db()
#         self.profile.refresh_from_db()
#         self.assertEqual(self.profile.about, self.profile_data['profile-about'])

#     def test_view_renders_correct_template(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(reverse('users:profile_update', kwargs={'username': self.user.username}))
#         self.assertTemplateUsed(response, '{0}/auth/profile_update.html'.format(MODULE_NAME))

#     def test_view_returns_correct_status_code(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(reverse('users:profile_update', kwargs={'username': self.user.username}))
#         self.assertEqual(response.status_code, 200)

#     def test_view_uses_correct_form(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(reverse('users:profile_update', kwargs={'username': self.user.username}))
#         self.assertIsInstance(response.context['form'], ProfileUpdateMultiForm)

#     def test_view_success_url(self):
#         self.login_test_user(self.user.username)
#         response = self.client.post(
#             reverse('users:profile_update', kwargs={'username': self.user.username}),
#             data=self.profile_data
#         )
#         self.assertRedirects(
#             response,
#             expected_url=reverse('users:profile_update', kwargs={'username': self.user.username}),
#             status_code=302,
#             target_status_code=200,
#             msg_prefix=''
#         )

#     def test_view_context_data(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(reverse('users:profile_update', kwargs={'username': self.user.username}))
#         self.assertEqual(response.context['gravatar_change_url'], settings.USERS_GRAVATAR_CHANGE_URL)

#     def test_view_ajax(self):
#         self.profile_data['profile-about'] = "I don't know"
#         kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
#         self.login_test_user(self.user.username)
#         response = self.client.post(
#             reverse('users:profile_update', kwargs={'username': self.user.username}),
#             data=self.profile_data,
#             **kwargs
#         )
#         self.profile.refresh_from_db()
#         self.assertEqual(self.profile.about, self.profile_data['profile-about'])
#         self.assertEqual(response.status_code, 200)
#         json_string = response.content.decode('utf-8')
#         response_data = json.loads(json_string)
#         self.assertEqual(_('message_success'), response_data['messages'][0]['message'])

#     def test_view_ajax_errors(self):
#         self.profile_data['user-first_name'] = ''
#         kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
#         self.login_test_user(self.user.username)
#         response = self.client.post(
#             reverse('users:profile_update', kwargs={'username': self.user.username}),
#             data=self.profile_data,
#             **kwargs
#         )
#         self.assertEqual(response.status_code, 400)
#         json_string = response.content.decode('utf-8')
#         response_data = json.loads(json_string)
#         self.assertEqual(_('message_error'), response_data['messages'][0]['message'])
#         self.assertEqual(response_data['errors']['fields']['first_name']['message'], [_('validation_field_required')])
