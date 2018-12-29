from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import resolve, reverse
from django.test import TestCase
from django.urls import path
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from ..conf import settings
from ..forms import LoginForm
from ..urls import urlpatterns
from ..views import LogoutView

User = get_user_model()

URL_PREFIX = 'accounts'


# Test view and url for testing redirect.
class TestLoginRequiredView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('Hello.')


urlpatterns += [
    path('test-login-required/', TestLoginRequiredView.as_view(), name='test_login_required')
]


class LoginViewTest(TestCase):

    def setUp(self):
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_user(
            username='cfs7',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@cfs.com',
            password=self.pwd
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)

    def test_login_view_renders_correct_template(self):
        response = self.client.get(reverse('security:login'))
        self.assertTemplateUsed(response, 'security/login.html')

    def test_login_view_returns_correct_status_code(self):
        response = self.client.get(reverse('security:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_view_uses_login_form(self):
        response = self.client.get(reverse('security:login'))
        self.assertIsInstance(response.context['form'], LoginForm)

    def test_view_redirects_if_user_authenticated(self):
        self.login_test_user(username=self.user.username)
        response = self.client.get(reverse('security:login'))
        self.assertRedirects(
            response,
            expected_url=reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_login_view_redirect_default(self):
        response = self.client.post(
            reverse('security:login'), {'username': self.user.username, 'password': self.pwd}
        )
        self.assertRedirects(
            response,
            expected_url=reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_login_required_redirected_to_login(self):
        response = self.client.get(reverse('security:test_login_required'), follow=True)
        self.assertRedirects(
            response,
            expected_url='{0}?next=/{1}/test-login-required/'.format(reverse(settings.LOGIN_URL), URL_PREFIX),
            target_status_code=200,
            msg_prefix=''
        )

    def test_login_view_redirect_with_next(self):
        next_url = reverse('security:test_login_required')

        # Context variable 'next' is set.
        url = '{0}?next={1}'.format(reverse(settings.LOGIN_URL), next_url)
        response = self.client.get(url)
        self.assertEqual(response.context['next'], next_url)

        # If next url is set, redirect to it upon successful login.
        response = self.client.post(
            reverse(settings.LOGIN_URL),
            {
                'username': self.user.username,
                'password': self.pwd,
                'next': next_url
            }
        )
        self.assertRedirects(
            response,
            expected_url=next_url,
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )

    def test_invalid_field(self):
        response = self.client.post(
            reverse('security:login'), {'username': '', 'password': ''}
        )
        self.assertFormError(response, 'form', 'username', _('validation_field_required'))
        self.assertFormError(response, 'form', 'password', _('validation_field_required'))

    def test_invalid_non_field(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            reverse('security:login'), {'username': self.user.username, 'password': self.pwd}
        )
        self.assertFormError(response, 'form', '__all__', _('validation_invalid_login'))

    def test_view_context_data(self):
        response = self.client.get(reverse('security:login'))
        self.assertEqual(response.context['next'], '')


class LogoutViewTest(TestCase):

    def test_logout_view_used(self):
        found = resolve(reverse('security:logout'))
        self.assertEqual(found.func.__name__, LogoutView.as_view().__name__)

    def test_logout_redirect(self):
        response = self.client.get(reverse('security:logout'))
        self.assertRedirects(
            response,
            expected_url=reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
            msg_prefix=''
        )
