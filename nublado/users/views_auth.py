from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView

from core.views import (
    ObjectSessionMixin, UserRequiredMixin
)
from .forms import UserPasswordResetForm
from .models import User

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


# class ProfileUpdateView(
#     LoginRequiredMixin, UserRequiredMixin,
#     CachedObjectMixin, AjaxMultiFormMixin,
#     ObjectSessionMixin, UpdateView
# ):
#     model = User
#     form_class = ProfileUpdateMultiForm
#     template_name = '{0}/auth/profile_update.html'.format(APP_NAME)
#     context_object_name = 'user_profile'

#     def get_form_kwargs(self):
#         kwargs = super(ProfileUpdateView, self).get_form_kwargs()
#         kwargs.update(instance={
#             'user': self.requested_user,
#             'profile': self.requested_user.profile,
#         })
#         return kwargs

#     def get_object(self, queryset=None):
#         return self.requested_user

#     def get_context_data(self, **kwargs):
#         context = super(ProfileUpdateView, self).get_context_data(**kwargs)
#         context['gravatar_img'] = settings.USERS_USE_GRAVATAR
#         context['gravatar_change_url'] = settings.USERS_GRAVATAR_CHANGE_URL
#         return context

#     def get_success_url(self):
#         return reverse('users:profile_update', kwargs={'username': self.kwargs['username']})
