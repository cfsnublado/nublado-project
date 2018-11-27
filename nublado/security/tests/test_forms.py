from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ..forms import LoginForm

User = get_user_model()


class LoginFormTest(TestCase):

    def setUp(self):
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_user(
            username='ale7',
            first_name='Alejandra',
            last_name='Acosta',
            email='ale7@foo.com',
            password=self.pwd
        )

    def tearDown(self):
        self.user.delete()

    def test_valid_data(self):
        form = LoginForm(data={'username': self.user.username, 'password': self.pwd})
        self.assertTrue(form.is_valid())

    def test_form_validation_with_user_not_found(self):
        form = LoginForm(data={'username': 'nonexistent', 'password': self.pwd})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], [_('validation_invalid_login')])

    def test_form_validation_blank_email(self):
        form = LoginForm(data={'username': '', 'password': self.pwd})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], [_('validation_field_required')])

    def test_form_validation_blank_password(self):
        form = LoginForm(data={'username': self.user.username, 'password': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'], [_('validation_field_required')])

    def test_form_validation_wrong_password(self):
        form = LoginForm(
            data={'username': self.user.username, 'password': '{0}{1}'.format(self.pwd, 'ax8*')}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], [_('validation_invalid_login')])

    def test_form_validation_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        form = LoginForm(data={'username': self.user.username, 'password': self.pwd})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], [_('validation_invalid_login')])
