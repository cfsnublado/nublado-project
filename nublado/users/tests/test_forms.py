from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ..forms import (
    ProfileUpdateForm, ProfileUserUpdateForm,
    UserForgotPasswordRequestForm, UserForgotPasswordResetForm,
    UserPasswordResetForm
)


User = get_user_model()


class UserForgotPasswordRequestFormTest(TestCase):

    def setUp(self):
        super(UserForgotPasswordRequestFormTest, self).setUp()
        self.form_data = {
            'email': 'foo@foo.com'
        }

    def test_valid_data(self):
        form = UserForgotPasswordRequestForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_validation_email(self):
        self.form_data['email'] = ''
        form = UserForgotPasswordRequestForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], [_('validation_field_required')])
        self.form_data['email'] = 'foofoo'
        form = UserForgotPasswordRequestForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], [_('validation_email_format')])


class UserForgotPasswordResetFormTest(TestCase):

    def setUp(self):
        super(UserForgotPasswordResetFormTest, self).setUp()
        self.pwd = 'Pizza?69p'
        self.changed_pwd = 'Coffee?69c'
        self.form_data = {
            'password1': self.changed_pwd,
            'password2': self.changed_pwd
        }
        self.user_data = {
            'username': 'cfs7',
            'email': 'ChristopherSanders78@gmail.com',
            'first_name': 'Christopher',
            'last_name': 'Sanders',
            'password': self.pwd
        }
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            password=self.user_data['password']
        )

    def test_valid_data(self):
        form = UserForgotPasswordResetForm(data=self.form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_form_save_returns_user(self):
        form = UserForgotPasswordResetForm(data=self.form_data, instance=self.user)
        user = form.save()
        self.assertEqual(user, self.user)

    def test_form_changes_user_password(self):
        pwd = self.user.password
        self.assertEqual(self.user.password, pwd)
        form = UserForgotPasswordResetForm(data=self.form_data, instance=self.user)
        form.save()
        self.assertNotEqual(self.user.password, pwd)
        self.assertFalse(self.client.login(username=self.user.username, password=self.pwd))
        self.assertTrue(self.client.login(username=self.user.username, password=self.changed_pwd))

    def test_form_invalid_for_blank_data(self):
        self.form_data['password1'] = ''
        form = UserForgotPasswordResetForm(data=self.form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password1'], [_('validation_field_required')])

    def test_form_validation_password(self):
        self.form_data['password1'] = 'aAaaAads8'
        form = UserForgotPasswordResetForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password1'], [_('validation_password_characters')])
        self.form_data['password1'] = 'aA8*!'
        form = UserForgotPasswordResetForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password1'], ['Password must contain at least 8 characters'])
        self.form_data['password1'] = '{0}{1}'.format(self.form_data['password2'], 'xxx')
        form = UserForgotPasswordResetForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], [_('validation_password_match')])


class UserPasswordResetFormTest(TestCase):

    def setUp(self):
        super(UserPasswordResetFormTest, self).setUp()
        self.pwd = 'Pizza?69p'
        self.changed_pwd = 'Coffee?69c'
        self.form_data = {
            'current_password': self.pwd,
            'password1': self.changed_pwd,
            'password2': self.changed_pwd
        }
        self.user_data = {
            'username': 'cfs7',
            'email': 'ChristopherSanders78@gmail.com',
            'first_name': 'Christopher',
            'last_name': 'Sanders',
            'password': self.pwd
        }
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            password=self.user_data['password']
        )

    def test_valid_data(self):
        form = UserPasswordResetForm(data=self.form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_form_save_returns_user(self):
        form = UserPasswordResetForm(data=self.form_data, instance=self.user)
        user = form.save()
        self.assertEqual(user, self.user)

    def test_form_changes_user_password(self):
        pwd = self.user.password
        self.assertEqual(self.user.password, pwd)
        form = UserPasswordResetForm(data=self.form_data, instance=self.user)
        form.save()
        self.assertNotEqual(self.user.password, pwd)
        self.assertFalse(self.client.login(username=self.user.username, password=self.pwd))
        self.assertTrue(self.client.login(username=self.user.username, password=self.changed_pwd))

    def test_form_invalid_for_blank_data(self):
        self.form_data['current_password'] = ''
        self.form_data['password1'] = ''
        form = UserPasswordResetForm(data=self.form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['current_password'], [_('validation_field_required')])
        self.assertEqual(form.errors['password1'], [_('validation_field_required')])

    def test_form_validation_password(self):
        self.form_data['password1'] = 'aAaaAads8'
        form = UserPasswordResetForm(data=self.form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password1'], [_('validation_password_characters')])
        self.form_data['password1'] = 'aA8*!'
        form = UserPasswordResetForm(data=self.form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password1'], ['Password must contain at least 8 characters'])
        self.form_data['password1'] = '{0}{1}'.format(self.form_data['password2'], 'xxx')
        form = UserPasswordResetForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], [_('validation_password_match')])

    def test_form_validation_invalid_current_password(self):
        self.form_data['current_password'] = 'ChamCham?69'
        form = UserPasswordResetForm(data=self.form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['current_password'], [_('validation_password_invalid')])


class ProfileUpdateFormTest(TestCase):

    def setUp(self):
        super(ProfileUpdateFormTest, self).setUp()
        self.user = User.objects.create_user(
            username='cfs',
            email='cfs@cfs.com',
            first_name='Christopher',
            last_name='Sanders',
            password='Pizza?69p'
        )
        self.profile = self.user.profile
        self.profile_data = {
            'about': 'Hello, my name is {0}. I like pizza.'.format(self.user.first_name)
        }

    def test_valid_data(self):
        form = ProfileUpdateForm(data=self.profile_data, instance=self.profile)
        profile = form.save()
        self.assertTrue(form.is_valid())
        self.assertEqual(profile.about, self.profile_data['about'])


class ProfileUserUpdateFormTest(TestCase):

    def setUp(self):
        super(ProfileUserUpdateFormTest, self).setUp()
        self.user = User.objects.create_user(
            username='cfs',
            email='cfs@cfs.com',
            first_name='Christopher',
            last_name='Sanders',
            password='Pizza?69p'
        )
        self.form_data = {
            'email': 'cfs@cfs.com',
            'first_name': 'Chris',
            'last_name': 'Sanders'
        }

    def test_valid_data(self):
        form = ProfileUserUpdateForm(data=self.form_data, instance=self.user)
        user = form.save()
        self.assertTrue(form.is_valid())
        self.assertEqual(user.first_name, self.form_data['first_name'])

    def test_form_validation_first_name(self):
        self.form_data['first_name'] = ''
        form = ProfileUserUpdateForm(data=self.form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['first_name'], [_('validation_field_required')])
        self.form_data['first_name'] = 'a@@  s'
        form = ProfileUserUpdateForm(data=self.form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['first_name'], [_('validation_user_name_characters')])

    def test_form_validation_last_name(self):
        self.form_data['last_name'] = ''
        form = ProfileUserUpdateForm(data=self.form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['last_name'], [_('validation_field_required')])
        self.form_data['last_name'] = 'a@@  s'
        form = ProfileUserUpdateForm(data=self.form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['last_name'], [_('validation_user_name_characters')])
