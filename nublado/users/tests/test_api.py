from rest_framework import status
from rest_framework.test import APITestCase

from django.utils.translation import ugettext_lazy as _
from django.urls import resolve, reverse

from ..models import User
from ..api.views_api import UserViewSet


class TestCommon(APITestCase):

    def setUp(self):
        self.pwd = 'Coffee?69c'
        self.user1 = User.objects.create_user(
            username='cham7',
            first_name='Cham',
            last_name='Cham',
            email='cham@cham.com',
            password=self.pwd,
            is_admin=True
        )
        self.user2 = User.objects.create_user(
            username='vero7',
            first_name='Veronica',
            last_name='Rodriguez',
            email='vero7@vero.com',
            password=self.pwd,
            is_admin=False
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)


class UserViewSetListTest(TestCommon):

    def test_correct_view_used(self):
        self.login_test_user(self.user1.username)
        found = resolve(reverse('api:user-list'))
        self.assertEqual(found.func.__name__, UserViewSet.as_view(actions='list').__name__)

    def test_user_permissions(self):
        # 403 with non authenticated user
        response = self.client.get(reverse('api:user-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # 403 with non-admin user
        self.login_test_user(self.user2.username)
        response = self.client.get(reverse('api:user-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()
        # 200 with admin
        self.login_test_user(self.user1.username)
        response = self.client.get(reverse('api:user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserViewSetDetailTest(TestCommon):

    def test_correct_view_used(self):
        self.login_test_user(self.user1.username)
        found = resolve(reverse('api:user-detail', kwargs={'username': self.user1.username}))
        self.assertEqual(found.func.__name__, UserViewSet.as_view(actions='retrieve').__name__)

    def test_user_permissions(self):
        # 403 with non authenticated user
        response = self.client.get(reverse('api:user-detail', kwargs={'username': self.user2.username}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # 403 with non-admin user
        self.login_test_user(self.user2.username)
        response = self.client.get(reverse('api:user-detail', kwargs={'username': self.user2.username}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()
        # 200 with admin
        self.login_test_user(self.user1.username)
        response = self.client.get(reverse('api:user-detail', kwargs={'username': self.user1.username}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserViewSetCreateTest(TestCommon):

    def setUp(self):
        super(UserViewSetCreateTest, self).setUp()
        self.user_data = {
            'username': 'soffie',
            'first_name': 'Soffie',
            'last_name': 'Valdez',
            'email': 'soffie@foo.com',
            'password': self.pwd,
            'confirm_password': self.pwd,
        }

    def test_correct_view_used(self):
        self.login_test_user(self.user1.username)
        found = resolve(reverse('api:user-list'))
        self.assertEqual(found.func.__name__, UserViewSet.as_view(actions='create').__name__)

    def test_user_permissions(self):
        # 403 with non authenticated user
        response = self.client.post(
            reverse('api:user-list'),
            self.user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # 403 with non-admin user
        self.login_test_user(self.user2.username)
        response = self.client.post(
            reverse('api:user-list'),
            self.user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()
        # 200 with admin
        self.login_test_user(self.user1.username)
        response = self.client.post(
            reverse('api:user-list'),
            self.user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_created(self):
        self.login_test_user(self.user1.username)
        self.assertFalse(User.objects.filter(username=self.user_data['username']).exists())
        response = self.client.post(
            reverse('api:user-list'),
            self.user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username=self.user_data['username']).exists())

    def test_validation_incomplete_data(self):
        self.login_test_user(self.user1.username)
        data = {'username': 'foo'}
        response = self.client.post(
            reverse('api:user-list'),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['first_name'][0]), _('validation_field_required'))
        self.assertEqual(str(response.data['last_name'][0]), _('validation_field_required'))
        self.assertEqual(str(response.data['password'][0]), _('validation_field_required'))


class UserViewSetUpdateTest(TestCommon):

    def test_correct_view_used(self):
        self.login_test_user(self.user1.username)
        found = resolve(reverse('api:user-detail', kwargs={'username': self.user1.username}))
        self.assertEqual(found.func.__name__, UserViewSet.as_view(actions='update').__name__)

    def test_user_permissions(self):
        data = {'email': 'foo@foo.com'}
        # 403 with non authenticated user
        response = self.client.patch(
            reverse('api:user-detail', kwargs={'username': self.user1.username}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # 403 with non-admin user
        self.login_test_user(self.user2.username)
        response = self.client.patch(
            reverse('api:user-detail', kwargs={'username': self.user1.username}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()
        # 200 with admin
        self.login_test_user(self.user1.username)
        data = {'email': 'fooooo@foo.com'}
        response = self.client.patch(
            reverse('api:user-detail', kwargs={'username': self.user1.username}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_validation_invalid_email(self):
        self.login_test_user(self.user1.username)
        data = {'email': 'foo'}
        response = self.client.patch(
            reverse('api:user-detail', kwargs={'username': self.user1.username}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'], [_('validation_email_format')])


class UserViewSetDeleteTest(TestCommon):
    pass

# class TestUserCreateReadView(TestCommon):

#     def setUp(self):
#         super(TestUserCreateReadView, self).setUp()
#         self.new_user_data = {
#             'username': 'ale7',
#             'email': 'ale7@ale.com',
#             'first_name': 'Alejandra',
#             'last_name': 'Acosta',
#             'password': self.pwd,
#             'confirm_password': self.pwd
#         }

#     def test_user_permissions(self):
#         # 403 with non authenticated user
#         response = self.client.get(reverse('api:users'))
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         response = self.client.post(reverse('api:users'), json.dumps(self.new_user_data), content_type='application/json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         # 403 with non-admin user
#         self.login_test_user(self.user2.username)
#         response = self.client.get(reverse('api:users'))
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         response = self.client.post(reverse('api:users'), json.dumps(self.new_user_data), content_type='application/json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.client.logout()
#         # 200 with admin
#         self.login_test_user(self.user1.username)
#         response = self.client.get(reverse('api:users'))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         response = self.client.post(reverse('api:users'), json.dumps(self.new_user_data), content_type='application/json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_correct_view_used(self):
#         self.login_test_user(self.user1.username)
#         found = resolve(reverse('api:users'))
#         self.assertEqual(found.func.__name__, UserCreateReadView.as_view().__name__)

#     def test_list_users(self):
#         self.login_test_user(self.user1.username)
#         response = self.client.get(reverse('api:users'))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         response_data = json.loads(response.content.decode())
#         self.assertEqual(len(response_data), 2)

#     def test_create_user(self):
#         self.login_test_user(self.user1.username)
#         response = self.client.post(reverse('api:users'), json.dumps(self.new_user_data), content_type='application/json')
#         response_data = json.loads(response.content.decode())
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(User.objects.count(), 3)
#         self.assertTrue(User.objects.filter(username=self.new_user_data['username']).exists())
#         user = User.objects.get(username=self.new_user_data['username'])
#         self.assertEqual(user.username, self.new_user_data['username'])
#         expected_response_data = {
#             'id': user.id,
#             'username': user.username,
#             'first_name': user.first_name,
#             'last_name': user.last_name,
#             'email': user.email,
#             'date_created': user.date_created.isoformat(),
#             'date_updated': user.date_updated.isoformat()
#         }
#         self.assertEqual(response_data, expected_response_data)

#     def test_validation_create_no_password(self):
#         self.login_test_user(self.user1.username)
#         self.new_user_data['password'] = ''
#         response = self.client.post(reverse('api:users'), json.dumps(self.new_user_data), content_type='application/json')
#         response_data = json.loads(response.content.decode())
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response_data['password'], ['This field may not be blank.'])

#     def test_validation_create_passwords_no_match(self):
#         self.login_test_user(self.user1.username)
#         self.new_user_data['confirm_password'] = 'asdf'
#         response = self.client.post(reverse('api:users'), json.dumps(self.new_user_data), content_type='application/json')
#         response_data = json.loads(response.content.decode())
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response_data['confirm_password'], [error_messages['password_match']])


# class TestUserReadUpdateDeleteView(TestCommon):

#     def setUp(self):
#         super(TestUserReadUpdateDeleteView, self).setUp()
#         self.user1_update_data = {
#             'username': 'cham7',
#             'first_name': 'Cham',
#             'last_name': 'Cham',
#             'email': 'cham@cham.com',
#         }

#     def test_user_permissions(self):
#         # 403 with non authenticated user
#         response = self.client.get(reverse('api:users', kwargs={'username': self.user1.username}), content_type='application/json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         response = self.client.put(
#             reverse('api:users', kwargs={'username': self.user1.username}),
#             data=json.dumps(self.user1_update_data),
#             content_type='application/json'
#         )
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         # 403 with non-admin user
#         self.login_test_user(self.user2.username)
#         response = self.client.get(reverse('api:users', kwargs={'username': self.user1.username}), content_type='application/json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         response = self.client.put(
#             reverse('api:users', kwargs={'username': self.user1.username}),
#             data=json.dumps(self.user1_update_data),
#             content_type='application/json'
#         )
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.client.logout()
#         # 200 with admin
#         self.login_test_user(self.user1.username)
#         response = self.client.get(reverse('api:users', kwargs={'username': self.user1.username}), content_type='application/json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         response = self.client.put(
#             reverse('api:users', kwargs={'username': self.user1.username}),
#             data=json.dumps(self.user1_update_data),
#             content_type='application/json'
#         )
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_correct_view_used(self):
#         self.login_test_user(self.user1.username)
#         found = resolve(reverse('api:users', kwargs={'username': self.user1.username}))
#         self.assertEqual(found.func.__name__, UserReadUpdateDeleteView.as_view().__name__)
