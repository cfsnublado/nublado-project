from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class TestUserManager(TestCase):

    def setUp(self):
        self.user_manager = User.objects
        self.pwd = 'Coffee?69c'

    def test_create_user_raises_error_with_no_username(self):
        with self.assertRaises(ValueError):
            self.user_manager.create_user(
                username='',
                first_name='Alejandra',
                last_name='Acosta',
                email='foo@foo.com',
                password=self.pwd
            )
        with self.assertRaises(ValueError):
            self.user_manager.create_user(
                email='foo@foo.com',
                first_name='Alejandra',
                last_name='Acosta',
                password=self.pwd
            )

    def test_create_user_raises_error_with_no_email(self):
        with self.assertRaises(ValueError):
            self.user_manager.create_user(
                username='ale7',
                first_name='Alejandra',
                last_name='Acosta',
                email='',
                password=self.pwd
            )
        with self.assertRaises(ValueError):
            self.user_manager.create_user(
                username='ale7',
                first_name='Alejandra',
                last_name='Acosta',
                password=self.pwd
            )

    def test_create_user_returns_user(self):
        user = self.user_manager.create_user(
            username='ale7',
            first_name='Alejandra',
            last_name='Acosta',
            email='ale7@foo.com',
            password=self.pwd
        )
        self.assertIsInstance(user, User)

    def test_create_user_with_extra_invalid_fields_throws_error(self):
        with self.assertRaises(TypeError):
            self.user_manager.create_user(
                username='ale7',
                first_name='Alejandra',
                last_name='Acosta',
                email='ale7@foo.com',
                password=self.pwd,
                foo='foo'
            )

    def test_create_superuser_returns_user_as_admin_and_superuser(self):
        user = self.user_manager.create_superuser(
            username='ale7',
            first_name='Alejandra',
            last_name='Acosta',
            email='ale7@foo.com',
            password=self.pwd
        )
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_superuser)

    def test_create_and_retrieve_user_from_db(self):
        user = self.user_manager.create_user(
            username='ale7',
            first_name='Alejandra',
            last_name='Acosta',
            email='ale7@foo.com',
            password=self.pwd
        )
        retrieved_user = User.objects.get(username='ale7')
        self.assertEqual(user, retrieved_user)

    def test_create(self):
        user = self.user_manager.create(
            username='ale7',
            first_name='Alejandra',
            last_name='Acosta',
            email='Ale7@Foo.com',
            password=self.pwd
        )
        retrieved_user = User.objects.get(username='ale7')
        self.assertEqual(user, retrieved_user)

    def test_create_inactive_incomplete_user(self):
        with self.assertRaises(ValueError):
            self.user_manager.create_inactive_incomplete_user(email='foo@foo.com')
        user = self.user_manager.create_inactive_incomplete_user(username='foo', email='foo@foo.com')
        self.assertFalse(user.is_active)
        self.assertEqual(user.username, 'foo')
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.last_name, '')
        self.assertEqual(user.password, '')

    def test_normalized_email(self):
        user1 = self.user_manager.create(
            username='ale7',
            first_name='Alejandra',
            last_name='Acosta',
            email='AleJaNdraAcosta@gmail.com',
            password=self.pwd
        )
        user2 = self.user_manager.create_user(
            username='cfs7',
            first_name='Christopher',
            last_name='Sanders',
            email='ChriStoPHErSanders78@gmail.com',
            password=self.pwd
        )
        self.assertEqual(user1.email, 'alejandraacosta@gmail.com')
        self.assertEqual(user2.email, 'christophersanders78@gmail.com')

    def test_normalized_username(self):
        user1 = self.user_manager.create(
            username='ALe7',
            first_name='Alejandra',
            last_name='Acosta',
            email='AleJaNdraAcosta@gmail.com',
            password=self.pwd
        )
        user2 = self.user_manager.create_user(
            username='CFs7',
            first_name='Christopher',
            last_name='Sanders',
            email='ChriStoPHErSanders78@gmail.com',
            password=self.pwd
        )

        self.assertEqual(user1.username, 'ale7')
        self.assertEqual(user2.username, 'cfs7')
