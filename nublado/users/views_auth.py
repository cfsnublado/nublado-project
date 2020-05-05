from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView

from core.views import (
    CachedObjectMixin, ObjectSessionMixin,
    UserRequiredMixin
)
from .forms import ProfileUpdateForm, UserPasswordResetForm
from .models import Profile, User

APP_NAME = apps.get_app_config('users').name


class UserPasswordResetView(
    LoginRequiredMixin, UserRequiredMixin,
    ObjectSessionMixin, UpdateView
):
    model = User
    form_class = UserPasswordResetForm
    template_name = '{0}/auth/password_reset.html'.format(APP_NAME)
    context_object_name = 'user_profile'
    confirmation_message = _('message_password_reset_success')

    def get_object(self, queryset=None):
        return self.requested_user

    def form_valid(self, form):
        messages.success(self.request, self.confirmation_message)
        return super(UserPasswordResetView, self).form_valid(form)

    def get_success_url(self):
        return reverse(settings.LOGIN_URL)


class ProfileUpdateView(
    LoginRequiredMixin, UserRequiredMixin,
    CachedObjectMixin, ObjectSessionMixin,
    UpdateView
):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = '{0}/auth/profile_update.html'.format(APP_NAME)
    context_object_name = 'user_profile'

    def get_object(self, queryset=None):
        return self.requested_user.profile

    def get_success_url(self):
        return reverse(
            'users:profile_view',
            kwargs={'username': self.kwargs['username']}
        )
