from django.core.exceptions import ValidationError
from django.test import TestCase

from ..validation import name_characters, password_characters


class TestCustomRegexValidators(TestCase):

    def test_password_characters(self):
        # at least 1 lowercase letter, 1 uppercase letter, 1 number, and a non-word symbol
        for password in ['asdfASDF!7', 'aA*7', 'aA$$*&#7']:
            password_characters(password)

        for password in ['asdf', 'asdfASDF', 'asdfASDF7', 'asdfASDF!', 'asA77! p']:
            with self.assertRaises(ValidationError, msg="{} didn't raise a ValidationError".format(password)):
                password_characters(password)

    def test_real_name_characters(self):
        # letters and single spaces
        for name in ['de la nada', 'arepa', 'áéíóúüñÁÉÍÓÚÑÜ', 'PaRaN gari Cutirimícuaro']:
            name_characters(name)

        for name in ['arepa7', 'de la  nada', 'asdfASDF7', 'name!']:
            with self.assertRaises(ValidationError, msg="{} didn't raise a ValidationError".format(name)):
                name_characters(name)
