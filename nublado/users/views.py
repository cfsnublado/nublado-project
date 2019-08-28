from django.apps import apps
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, FormView, UpdateView

from core.utils import send_user_token_email
from .conf import settings
from .forms import UserForgotPasswordRequestForm, UserForgotPasswordResetForm
from .models import User


APP_NAME = apps.get_app_config('users').name


class IsUserMixin(object):
    is_user = False

    def get_object(self, queryset=None):
        user = get_object_or_404(User, username=self.kwargs['username'])
        if user.id == self.request.user.id:
            self.is_user = True
        return user

    def get_context_data(self, **kwargs):
        context = super(IsUserMixin, self).get_context_data(**kwargs)
        context['is_user'] = self.is_user
        return context


class UserForgotPasswordRequestView(FormView):
    template_name = '{0}/password_reset_request.html'.format(APP_NAME)
    form_class = UserForgotPasswordRequestForm
    confirmation_message = _('msg_password_reset_request_confirmation')

    def dispatch(self, request, *args, **kwargs):
        # If user is already logged in, redirect.
        if request.user.is_authenticated:
            return redirect(reverse(settings.LOGIN_REDIRECT_URL))
        return super(UserForgotPasswordRequestView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            send_user_token_email(
                user=user,
                request=self.request,
                subject_template_name='{0}/{1}'.format(APP_NAME, 'password_reset_request_subject.txt'),
                email_template_name='{0}/{1}'.format(APP_NAME, 'password_reset_request_email.html'),
                extra_email_context={'username': user.username}
            )
            messages.success(self.request, self.confirmation_message)
        except User.DoesNotExist:
            pass
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(settings.PROJECT_HOME_URL)


class UserForgotPasswordResetView(UpdateView):
    model = User
    form_class = UserForgotPasswordResetForm
    template_name = '{0}/forgot_password_reset.html'.format(APP_NAME)
    confirmation_message = _('user_password_reset_success_msg')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(
                reverse(settings.LOGIN_REDIRECT_URL)
            )
        return super(UserForgotPasswordResetView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            uid = urlsafe_base64_decode(self.kwargs['uidb64']).decode()
            token = self.kwargs['token']
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is None or not default_token_generator.check_token(user, token):
            raise Http404()
        return user

    def form_valid(self, form):
        messages.success(self.request, self.confirmation_message)
        return super(UserForgotPasswordResetView, self).form_valid(form)

    def get_success_url(self):
        return reverse(settings.PROJECT_HOME_URL)


class ProfileDetailView(IsUserMixin, DetailView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = '{0}/profile_view.html'.format(APP_NAME)
    context_object_name = 'user_profile'

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        context['profile'] = self.object.profile
        return context
