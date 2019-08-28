from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, View

from .conf import settings
from .forms import LoginForm


class LoginView(FormView):
    '''
    Provides the ability to login as a user with a username and password
    '''
    form_class = LoginForm
    redirect_field_name = REDIRECT_FIELD_NAME
    redirect_next_url = None
    template_name = 'security/login.html'

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        self.redirect_next_url = request.GET.get(self.redirect_field_name, '')
        # If user already logged in, redirect.
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse(settings.LOGIN_REDIRECT_URL))
        # Sets a test cookie to make sure the user has cookies enabled.
        request.session.set_test_cookie()
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        # If the test cookie worked, go ahead and
        # delete it since it's no longer needed.
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
        return super(LoginView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get(self.redirect_field_name, '')
        return context

    def get_success_url(self):
        redirect_to = self.request.POST.get('next', '')
        url_is_safe = is_safe_url(redirect_to, allowed_hosts={settings.PROJECT_DOMAIN})
        if redirect_to and url_is_safe:
            return redirect_to
        else:
            return reverse(settings.LOGIN_REDIRECT_URL)


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponseRedirect(reverse(settings.LOGOUT_REDIRECT_URL))
