from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_('label_username'),
        required=True,
        error_messages={
            'required': _('validation_field_required'),
        }
    )
    password = forms.CharField(
        label=_('label_password'),
        widget=forms.PasswordInput,
        error_messages={
            'required': _('validation_field_required'),
        }
    )
    error_messages = {
        'invalid_login': _('validation_invalid_login'),
        'inactive': _('validation_inactive_user')
    }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('auto_id', '%s')
        kwargs.setdefault('label_suffix', '')
        super(LoginForm, self).__init__(*args, **kwargs)
