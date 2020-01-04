from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Profile, User
from .validation import (
    help_texts, password_characters,
    password_min_length
)


class UserFormCommon(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        error_messages = {
            'username': {
                'required': _('validation_field_required'),
                'unique': _('validation_username_unique'),
            },
            'email': {
                'required': _('validation_field_required'),
                'unique': _('validation_email_unique'),
                'invalid': _('validation_email_format')
            },
            'first_name': {
                'required': _('validation_field_required'),
            },
            'last_name': {
                'required': _('validation_field_required'),
            },
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        return first_name.title()

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        return last_name.title()


class PasswordResetForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_('label_password'),
        widget=forms.PasswordInput,
        error_messages={
            'required': _('validation_field_required')
        },
        validators=[password_min_length, password_characters],
        help_text=help_texts['password']
    )
    password2 = forms.CharField(
        label=_('label_password_confirm'),
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta:
        model = User
        fields = []

    def save(self):
        user = super(PasswordResetForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.save()
        return user

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password1 != password2:
            raise forms.ValidationError(_('validation_password_match'))
        return password2


class UserPasswordResetForm(PasswordResetForm):
    current_password = forms.CharField(
        label=_('label_current_password'),
        widget=forms.PasswordInput,
        error_messages={
            'required': _('validation_field_required')
        },
    )

    def __init__(self, *args, **kwargs):
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['password1'].label = _('label_new_password')
        self.fields['password2'].label = _('label_new_password_confirm')

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password', None)
        if not self.instance.check_password(current_password):
            raise forms.ValidationError(_('validation_password_invalid'))
        return current_password


class UserForgotPasswordRequestForm(forms.Form):
    email = forms.EmailField(
        label=_('label_email'),
        max_length=254,
        required=True,
        error_messages={
            'required': _('validation_field_required'),
            'invalid': _('validation_email_format')
        }
    )

    def clean_email(self):
        return self.cleaned_data['email'].lower()


class UserForgotPasswordResetForm(PasswordResetForm):
    pass


class ProfileUserUpdateForm(UserFormCommon):
    class Meta(UserFormCommon.Meta):
        fields = ['email', 'first_name', 'last_name']


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['about']
