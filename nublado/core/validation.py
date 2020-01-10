from django.core.validators import (EmailValidator, MinLengthValidator,
                                    RegexValidator)
from django.utils.translation import ugettext_lazy as _

from .utils import format_lazy

PASSWORD_MIN_LENGTH = 8
USERNAME_MIN_LENGTH = 3

help_texts = {
    'password': _('help_text_password'),
}

# only letters (Spanish characters included) and single spaces.
name_characters = RegexValidator(
    regex=r'^([a-zA-ZáéíóúüñÁÉÍÓÚÜÑ.]+ ?)+$',
    message=_('validation_user_name_characters'),
    code='characters'
)

email_format = EmailValidator(
    message=_('validation_email_format'),
    code='email'
)

password_min_length = MinLengthValidator(
    PASSWORD_MIN_LENGTH,
    message=format_lazy(
        _('validation_password_min_length {min_len}'),
        min_len=PASSWORD_MIN_LENGTH
    )
)

# at least 1 uppercase letter, 1 lowercase letter, 1 number, and 1 symbol
password_characters = RegexValidator(
    regex=r'^(?=\S*[a-z])(?=\S*[A-Z])(?=\S*[\d])(?=\S*[\W])\S*$',
    message=_('validation_password_characters'),
    code='characters'
)

# lowercase alphanumeric characters
username_characters = RegexValidator(
    regex=r'^[0-9a-z-]*$',
    message=_('validation_username_characters'),
    code='characters'
)

username_min_length = MinLengthValidator(
    USERNAME_MIN_LENGTH,
    message=format_lazy(
        _('validation_username_min_length {min_len}'),
        min_len=USERNAME_MIN_LENGTH
    )
)


def validate_translation_languages(obj, error, language=None):
    '''
    Checks if a language is in a model's translations' languages.
    If so, raise an error.

    obj: Object that inherits from LanguageModel. If obj is parent, it must have a
         One to Many relation named translations, also inheriting from LanguageModel
    error: Instance of error to be raised (e.g., ValidationError)
    '''
    if language is None:
        language = obj.language
    if obj.parent:
        if language == obj.parent.language:
            raise error
    else:
        translation_languages = obj.translations.values_list('language', flat=True)
        if language in translation_languages:
            raise error
