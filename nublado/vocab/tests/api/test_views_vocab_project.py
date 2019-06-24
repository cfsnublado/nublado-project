import json

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status as drf_status
from rest_framework.viewsets import ModelViewSet

from core.api.views_api import APIDefaultsMixin
from vocab.api.pagination import SmallPagination
from vocab.api.permissions import ProjectOwnerPermission, ReadPermission
from vocab.api.views_vocab_project import VocabProjectViewSet
from vocab.models import VocabProject
from vocab.serializers import VocabProjectSerializer
from .base_test import TestCommon

User = get_user_model()


class VocabProjectViewSetTest(TestCommon):

    def setUp(self):
        super(VocabProjectViewSetTest, self).setUp()
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.user_2 = User.objects.create_user(
            username='abc',
            first_name='Christopher',
            last_name='Sanders',
            email='abc@foo.com',
            password=self.pwd
        )

    def get_project_serializer_data(self, project):
        serializer = VocabProjectSerializer(
            project,
            context={'request': self.get_dummy_request()}
        )
        return json.loads(serializer.json_data())

    def test_view_setup(self):
        view = VocabProjectViewSet()
        self.assertEqual('pk', view.lookup_field)
        self.assertEqual('pk', view.lookup_url_kwarg)
        self.assertEqual(VocabProjectSerializer, view.serializer_class)
        self.assertCountEqual(VocabProject.objects.all(), view.queryset)
        self.assertEqual(SmallPagination, view.pagination_class)

        permission_classes = [ReadPermission, ProjectOwnerPermission]

        self.assertEqual(permission_classes, view.permission_classes)

    def test_inheritance(self):
        classes = (
            APIDefaultsMixin,
            ModelViewSet
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabProjectViewSet, class_name))

    def test_view_create(self):
        vocab_project_data = {
            'name': 'another test project',
            'description': 'another test project'
        }

        self.login_test_user(self.user.username)

        self.assertFalse(
            VocabProject.objects.filter(name=vocab_project_data['name']).exists()
        )

        response = self.client.post(
            reverse('api:vocab-project-list'),
            data=vocab_project_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_201_CREATED)
        self.assertTrue(
            VocabProject.objects.filter(
                owner=self.user,
                name=vocab_project_data['name']
            ).exists()
        )

    def test_view_detail(self):
        response = self.client.get(
            reverse(
                'api:vocab-project-detail',
                kwargs={'pk': self.vocab_project.id}
            ),
        )
        data = self.get_project_serializer_data(self.vocab_project)
        self.assertEqual(
            data,
            json.loads(response.content)
        )

    def test_view_list(self):
        vocab_project_2 = VocabProject.objects.create(
            owner=self.user,
            name='test project 2'
        )
        data_1 = self.get_project_serializer_data(self.vocab_project)
        data_2 = self.get_project_serializer_data(vocab_project_2)
        response = self.client.get(
            reverse('api:vocab-project-list')
        )
        expected_results = json.dumps({
            "next": None,
            "previous": None,
            "page_num": 1,
            "count": 2,
            "num_pages": 1,
            "results": [data_1, data_2]
        })

        self.assertCountEqual(json.loads(expected_results), json.loads(response.content))

    def test_view_update(self):
        self.login_test_user(self.user.username)

        vocab_project_data = {'name': 'goodbye'}

        self.assertNotEqual(
            self.vocab_project.name,
            vocab_project_data['name']
        )

        response = self.client.put(
            reverse(
                'api:vocab-project-detail',
                kwargs={'pk': self.vocab_project.id}
            ),
            data=json.dumps(vocab_project_data),
            content_type='application/json'
        )

        self.vocab_project.refresh_from_db()
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)
        self.assertEqual(
            self.vocab_project.name,
            vocab_project_data['name']
        )

    def test_view_delete(self):
        self.login_test_user(self.user.username)

        id = self.vocab_project.id

        self.assertTrue(VocabProject.objects.filter(id=id).exists())
        self.client.delete(
            reverse('api:vocab-project-detail', kwargs={'pk': self.vocab_project.id})
        )
        self.assertFalse(VocabProject.objects.filter(id=id).exists())

    # View permissions
    def test_permissions_create(self):
        vocab_project_data = {
            'name': 'another test project',
            'description': 'another test project'
        }

        # Not authenticated
        self.client.logout()

        response = self.client.post(
            reverse('api:vocab-project-list'),
            data=vocab_project_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated
        self.login_test_user(self.user.username)

        response = self.client.post(
            reverse('api:vocab-project-list'),
            data=vocab_project_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_201_CREATED)

    def test_permissions_retrieve(self):
        # Not authenticated
        self.client.logout()

        response = self.client.get(
            reverse(
                'api:vocab-project-detail',
                kwargs={'pk': self.vocab_project.id}
            ),
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_permissions_list(self):
        # Not authenticated
        self.client.logout()

        response = self.client.get(
            reverse(
                'api:vocab-project-list'
            ),
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_permissions_update(self):
        vocab_project_data = {'name': 'goodbye'}

        # Not authenticated
        self.client.logout()

        response = self.client.put(
            reverse(
                'api:vocab-project-detail',
                kwargs={'pk': self.vocab_project.id}
            ),
            data=json.dumps(vocab_project_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated non-owner
        self.login_test_user(self.user_2.username)

        response = self.client.put(
            reverse(
                'api:vocab-project-detail',
                kwargs={'pk': self.vocab_project.id}
            ),
            data=json.dumps(vocab_project_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Owner
        self.client.logout()
        self.login_test_user(self.user.username)

        response = self.client.put(
            reverse(
                'api:vocab-project-detail',
                kwargs={'pk': self.vocab_project.id}
            ),
            data=json.dumps(vocab_project_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

        # Non-owner superuser
        self.client.logout()
        self.login_test_user(self.superuser.username)

        response = self.client.put(
            reverse(
                'api:vocab-project-detail',
                kwargs={'pk': self.vocab_project.id}
            ),
            data=json.dumps(vocab_project_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_permissions_delete(self):
        # Not authenticated
        self.client.logout()

        response = self.client.delete(
            reverse('api:vocab-project-detail', kwargs={'pk': self.vocab_project.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated
        self.login_test_user(self.user_2.username)

        response = self.client.delete(
            reverse('api:vocab-project-detail', kwargs={'pk': self.vocab_project.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Owner
        self.client.logout()
        self.login_test_user(self.user.username)

        response = self.client.delete(
            reverse('api:vocab-project-detail', kwargs={'pk': self.vocab_project.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_204_NO_CONTENT)

        # Non-owner superuser
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )

        self.client.logout()
        self.login_test_user(self.superuser.username)

        response = self.client.delete(
            reverse('api:vocab-project-detail', kwargs={'pk': self.vocab_project.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_204_NO_CONTENT)
