import json

from rest_framework import status as drf_status
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin,
    RetrieveModelMixin, UpdateModelMixin
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from django.contrib.auth import get_user_model
from django.urls import resolve, reverse
from django.test import RequestFactory, TestCase

from core.api.views_api import APIDefaultsMixin
from ..api.pagination import LargePagination, SmallPagination
from ..api.permissions import (
    CreatorPermission, IsSuperuser, OwnerPermission,
    ReadPermission, ReadWritePermission
)
from ..api.views_vocab_context import (
    NestedVocabContextViewSet, NestedVocabSourceViewSet,
    VocabContextViewSet, VocabContextEntryViewSet,
)
from ..api.views_vocab_entry import (
    VocabEntryViewSet, VocabEntryExportView,
    VocabEntryLanguageExportView, VocabEntryImportView
)
from ..api.views_mixins import BatchMixin
from ..api.views_project import VocabProjectViewSet
from ..api.views_vocab_source import (
    NestedVocabSourceViewSet, VocabSourceExportView, VocabSourceImportView,
    VocabSourceViewSet, VocabSourceEntryViewSet
)
from ..conf import settings
from ..models import (
    VocabContext, VocabContextEntry, VocabEntry,
    VocabProject, VocabSource
)
from ..serializers import (
    VocabContextSerializer, VocabContextEntrySerializer, VocabEntrySerializer,
    VocabProjectSerializer, VocabSourceSerializer
)
from ..utils import export_vocab_entries, export_vocab_source

User = get_user_model()

APP_NAME = 'vocab'
URL_PREFIX = getattr(settings, 'VOCAB_URL_PREFIX')


class TestCommon(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_user(
            username='cfs',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@foo.com',
            password=self.pwd
        )
        self.superuser = User.objects.create_superuser(
            username='superuser',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs777@foo.com',
            password=self.pwd
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)

    def get_dummy_request(self):
        request = self.request_factory.get('/fake-path')
        request.user = self.user
        return request


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

        permission_classes = [ReadPermission, OwnerPermission]

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


class VocabSourceViewSetTest(TestCommon):

    def setUp(self):
        super(VocabSourceViewSetTest, self).setUp()

        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source'
        )
        self.user_2 = User.objects.create_user(
            username='abc',
            first_name='Christopher',
            last_name='Sanders',
            email='abc@foo.com',
            password=self.pwd
        )

    def get_source_serializer_data(self, source):
        serializer = VocabSourceSerializer(
            source,
            context={'request': self.get_dummy_request()}
        )
        return json.loads(serializer.json_data())

    def test_view_setup(self):
        view = VocabSourceViewSet()

        self.assertEqual('pk', view.lookup_field)
        self.assertEqual('pk', view.lookup_url_kwarg)
        self.assertEqual(VocabSourceSerializer, view.serializer_class)
        self.assertCountEqual(
            VocabSource.objects.select_related('vocab_project').prefetch_related('vocab_contexts'), view.queryset
        )
        self.assertEqual(SmallPagination, view.pagination_class)

        permission_classes = [ReadPermission, CreatorPermission]

        self.assertEqual(permission_classes, view.permission_classes)

    def test_inheritance(self):
        classes = (
            APIDefaultsMixin,
            RetrieveModelMixin,
            UpdateModelMixin,
            DestroyModelMixin,
            ListModelMixin,
            GenericViewSet
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceViewSet, class_name))

    def test_view_detail(self):
        response = self.client.get(
            reverse(
                'api:vocab-source-detail',
                kwargs={'pk': self.vocab_source.id}
            ),
        )
        data = self.get_source_serializer_data(self.vocab_source)

        self.assertEqual(
            data,
            json.loads(response.content)
        )

    def test_view_list(self):
        vocab_project_2 = VocabProject.objects.create(
            owner=self.user,
            name='test project 2'
        )
        vocab_source_2 = VocabSource.objects.create(
            vocab_project=vocab_project_2,
            creator=self.user,
            name='test source 2'
        )
        data_1 = self.get_source_serializer_data(self.vocab_source)
        data_2 = self.get_source_serializer_data(vocab_source_2)
        expected_results = json.dumps({
            "next": None,
            "previous": None,
            "page_num": 1,
            "count": 2,
            "num_pages": 1,
            "results": [data_1, data_2]
        })
        response = self.client.get(
            reverse('api:vocab-source-list')
        )

        self.assertCountEqual(json.loads(expected_results), json.loads(response.content))

    def test_view_update(self):
        self.login_test_user(self.user.username)

        vocab_source_data = {'name': 'updated source name'}

        self.assertNotEqual(
            self.vocab_source.name,
            vocab_source_data['name']
        )

        response = self.client.put(
            reverse(
                'api:vocab-source-detail',
                kwargs={'pk': self.vocab_source.id}
            ),
            data=json.dumps(vocab_source_data),
            content_type='application/json'
        )
        self.vocab_source.refresh_from_db()

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)
        self.assertEqual(
            self.vocab_source.name,
            vocab_source_data['name']
        )

    def test_view_delete(self):
        self.login_test_user(self.user.username)

        id = self.vocab_source.id

        self.assertTrue(VocabSource.objects.filter(id=id).exists())
        self.client.delete(
            reverse('api:vocab-source-detail', kwargs={'pk': self.vocab_source.id})
        )
        self.assertFalse(VocabSource.objects.filter(id=id).exists())

    # View permissions
    def test_permissions_retrieve(self):
        # Not authenticated
        self.client.logout()

        response = self.client.get(
            reverse(
                'api:vocab-source-detail',
                kwargs={'pk': self.vocab_source.id}
            ),
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_permissions_list(self):
        # Not authenticated
        self.client.logout()

        response = self.client.get(
            reverse(
                'api:vocab-source-list'
            ),
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_permissions_update(self):
        vocab_source_data = {'name': 'updated source name'}

        # Not authenticated
        self.client.logout()

        response = self.client.put(
            reverse(
                'api:vocab-source-detail',
                kwargs={'pk': self.vocab_source.id}
            ),
            data=json.dumps(vocab_source_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated non-creator
        self.login_test_user(self.user_2.username)

        response = self.client.put(
            reverse(
                'api:vocab-source-detail',
                kwargs={'pk': self.vocab_source.id}
            ),
            data=json.dumps(vocab_source_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Creator
        self.client.logout()
        self.login_test_user(self.user.username)

        response = self.client.put(
            reverse(
                'api:vocab-source-detail',
                kwargs={'pk': self.vocab_source.id}
            ),
            data=json.dumps(vocab_source_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

        # Non-creator superuser
        self.client.logout()
        self.login_test_user(self.superuser.username)

        response = self.client.put(
            reverse(
                'api:vocab-source-detail',
                kwargs={'pk': self.vocab_source.id}
            ),
            data=json.dumps(vocab_source_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_permissions_delete(self):
        # Not authenticated
        self.client.logout()

        response = self.client.delete(
            reverse('api:vocab-source-detail', kwargs={'pk': self.vocab_source.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated non-creator
        self.login_test_user(self.user_2.username)

        response = self.client.delete(
            reverse('api:vocab-source-detail', kwargs={'pk': self.vocab_source.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Creator
        self.client.logout()
        self.login_test_user(self.user.username)

        response = self.client.delete(
            reverse('api:vocab-source-detail', kwargs={'pk': self.vocab_source.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_204_NO_CONTENT)

        # Non-creator superuser
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source'
        )

        self.client.logout()
        self.login_test_user(self.superuser.username)

        response = self.client.delete(
            reverse('api:vocab-source-detail', kwargs={'pk': self.vocab_source.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_204_NO_CONTENT)


class NestedVocabSourceViewSetTest(TestCommon):

    def setUp(self):
        super(NestedVocabSourceViewSetTest, self).setUp()
        self.user_2 = User.objects.create_user(
            username='abc',
            first_name='Christopher',
            last_name='Sanders',
            email='abc@foo.com',
            password=self.pwd
        )
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_project_2 = VocabProject.objects.create(
            owner=self.user,
            name='test project 2'
        )
        self.vocab_source_1 = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source 1'
        )
        self.vocab_source_2 = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source 2'
        )
        self.vocab_source_3 = VocabSource.objects.create(
            vocab_project=self.vocab_project_2,
            creator=self.user,
            name='test source 3'
        )
        self.vocab_source_4 = VocabSource.objects.create(
            vocab_project=self.vocab_project_2,
            creator=self.user,
            name='test source 4'
        )

    def get_source_serializer_data(self, source):
        serializer = VocabSourceSerializer(
            source,
            context={'request': self.get_dummy_request()}
        )

        return json.loads(serializer.json_data())

    def test_view_setup(self):
        view = NestedVocabSourceViewSet()
        self.assertEqual('pk', view.lookup_field)
        self.assertEqual('pk', view.lookup_url_kwarg)
        self.assertEqual(VocabSourceSerializer, view.serializer_class)
        self.assertIsNone(view.vocab_project)
        self.assertCountEqual(
            VocabSource.objects.select_related('vocab_project').prefetch_related('vocab_contexts'),
            view.queryset
        )
        self.assertEqual(SmallPagination, view.pagination_class)

        permission_classes = [ReadPermission, OwnerPermission]

        self.assertEqual(permission_classes, view.permission_classes)

    def test_inheritance(self):
        classes = (
            APIDefaultsMixin,
            BatchMixin,
            CreateModelMixin,
            ListModelMixin,
            GenericViewSet
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(NestedVocabSourceViewSet, class_name)
            )

    def test_view_create(self):
        self.login_test_user(self.user.username)

        vocab_source_data = {
            'name': 'another test source'
        }
        self.assertFalse(
            VocabSource.objects.filter(
                name=vocab_source_data['name']
            ).exists()
        )
        self.client.post(
            reverse(
                'api:nested-vocab-source-list',
                kwargs={'vocab_project_pk': self.vocab_project.id}
            ),
            data=vocab_source_data
        )
        self.assertTrue(
            VocabSource.objects.filter(
                creator=self.user,
                name=vocab_source_data['name']
            ).exists()
        )

    def test_view_list(self):
        # Project 1
        data_1 = self.get_source_serializer_data(self.vocab_source_1)
        data_2 = self.get_source_serializer_data(self.vocab_source_2)
        expected_results = json.dumps({
            "next": None,
            "previous": None,
            "page_num": 1,
            "count": 2,
            "num_pages": 1,
            "results": [data_1, data_2]
        })
        response = self.client.get(
            reverse(
                'api:nested-vocab-source-list',
                kwargs={'vocab_project_pk': self.vocab_project.id}
            )
        )

        self.assertCountEqual(json.loads(expected_results), json.loads(response.content))

        # Project 2
        data_3 = self.get_source_serializer_data(self.vocab_source_3)
        data_4 = self.get_source_serializer_data(self.vocab_source_4)
        expected_results = json.dumps({
            "next": None,
            "previous": None,
            "page_num": 1,
            "count": 2,
            "num_pages": 1,
            "results": [data_3, data_4]
        })
        response = self.client.get(
            reverse(
                'api:nested-vocab-source-list',
                kwargs={'vocab_project_pk': self.vocab_project_2.id}
            )
        )

    def test_permissions_list(self):
        # Not authenticated
        self.client.logout()
        response = self.client.get(
            reverse(
                'api:nested-vocab-source-list',
                kwargs={'vocab_project_pk': self.vocab_project.id}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_permissions_create(self):
        vocab_source_data = {
            'name': 'another test source'
        }

        # Not authenticated
        self.client.logout()
        response = self.client.post(
            reverse(
                'api:nested-vocab-source-list',
                kwargs={'vocab_project_pk': self.vocab_project.id}
            ),
            data=vocab_source_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated non owner
        self.login_test_user(self.user_2.username)

        response = self.client.post(
            reverse(
                'api:nested-vocab-source-list',
                kwargs={'vocab_project_pk': self.vocab_project.id}
            ),
            data=vocab_source_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Owner
        self.client.logout()
        self.login_test_user(self.user.username)

        response = self.client.post(
            reverse(
                'api:nested-vocab-source-list',
                kwargs={'vocab_project_pk': self.vocab_project.id}
            ),
            data=vocab_source_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_201_CREATED)

        # Non-owner superuser
        self.client.logout()
        self.login_test_user(self.superuser.username)

        vocab_source_data = {
            'name': 'yet another test source'
        }

        response = self.client.post(
            reverse(
                'api:nested-vocab-source-list',
                kwargs={'vocab_project_pk': self.vocab_project.id}
            ),
            data=vocab_source_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_201_CREATED)


class VocabEntryViewSetTest(TestCommon):

    def setUp(self):
        super(VocabEntryViewSetTest, self).setUp()
        self.vocab_entry = VocabEntry.objects.create(
            language='en',
            entry='hello'
        )

    def get_entry_serializer_data(self, entry):
        serializer = VocabEntrySerializer(
            entry,
            context={'request': self.get_dummy_request()}
        )
        return json.loads(serializer.json_data())

    def test_view_setup(self):
        view = VocabEntryViewSet()
        self.assertEqual('pk', view.lookup_field)
        self.assertEqual('pk', view.lookup_url_kwarg)
        self.assertEqual(VocabEntrySerializer, view.serializer_class)
        self.assertEqual(LargePagination, view.pagination_class)

        permission_classes = [ReadWritePermission]

        self.assertEqual(permission_classes, view.permission_classes)

    def test_inheritance(self):
        classes = (
            APIDefaultsMixin,
            BatchMixin,
            ModelViewSet
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntryViewSet, class_name))

    def test_view_create(self):
        self.login_test_user(self.user.username)

        vocab_entry_data = {
            'language': 'es',
            'entry': 'tergiversar'
        }

        self.assertFalse(
            VocabEntry.objects.filter(
                language=vocab_entry_data['language'],
                entry=vocab_entry_data['entry']
            ).exists()
        )
        self.client.post(
            reverse('api:vocab-entry-list'),
            data=vocab_entry_data
        )
        self.assertTrue(
            VocabEntry.objects.filter(
                language=vocab_entry_data['language'],
                entry=vocab_entry_data['entry']
            ).exists()
        )

    def test_view_detail(self):
        response = self.client.get(
            reverse(
                'api:vocab-entry-detail',
                kwargs={'pk': self.vocab_entry.id}
            ),
        )
        data = self.get_entry_serializer_data(self.vocab_entry)

        self.assertEqual(
            data,
            json.loads(response.content)
        )

    def test_view_list(self):
        vocab_entry_2 = VocabEntry.objects.create(
            language='es',
            entry='hola'
        )
        data_1 = self.get_entry_serializer_data(self.vocab_entry)
        data_2 = self.get_entry_serializer_data(vocab_entry_2)
        response = self.client.get(
            reverse('api:vocab-entry-list')
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

        vocab_entry_data = {'entry': 'goodbye'}

        self.assertNotEqual(
            self.vocab_entry.entry,
            vocab_entry_data['entry']
        )

        response = self.client.put(
            reverse(
                'api:vocab-entry-detail',
                kwargs={'pk': self.vocab_entry.id}
            ),
            data=json.dumps(vocab_entry_data),
            content_type='application/json'
        )

        self.vocab_entry.refresh_from_db()
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)
        self.assertEqual(
            self.vocab_entry.entry,
            vocab_entry_data['entry']
        )

    def test_view_delete(self):
        self.login_test_user(self.user.username)

        id = self.vocab_entry.id

        self.assertTrue(VocabEntry.objects.filter(id=id).exists())
        self.client.delete(
            reverse('api:vocab-entry-detail', kwargs={'pk': self.vocab_entry.id})
        )
        self.assertFalse(VocabEntry.objects.filter(id=id).exists())

    def test_view_detail_querystring(self):
        vocab_entry_2 = VocabEntry.objects.create(
            language='es',
            entry='tergiversar'
        )
        response = self.client.get(
            reverse('api:vocab-entry-detail-data'),
            {
                'language': self.vocab_entry.language,
                'entry': self.vocab_entry.entry
            }
        )
        data = self.get_entry_serializer_data(self.vocab_entry)

        self.assertEqual(
            data,
            json.loads(response.content)
        )

        response = self.client.get(
            reverse('api:vocab-entry-detail-data'),
            {
                'language': vocab_entry_2.language,
                'entry': vocab_entry_2.entry
            }
        )
        data = self.get_entry_serializer_data(vocab_entry_2)

        self.assertEqual(
            data,
            json.loads(response.content)
        )

    # View permissions
    def test_permissions_create(self):
        vocab_entry_data = {
            'language': 'es',
            'entry': 'tergiversar'
        }

        # Not authenticated
        self.client.logout()

        response = self.client.post(
            reverse('api:vocab-entry-list'),
            data=vocab_entry_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated
        self.login_test_user(self.user.username)

        response = self.client.post(
            reverse('api:vocab-entry-list'),
            data=vocab_entry_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_201_CREATED)

    def test_permissions_update(self):
        vocab_entry_data = {'entry': 'goodbye'}

        # Not authenticated
        self.client.logout()

        response = self.client.put(
            reverse(
                'api:vocab-entry-detail',
                kwargs={'pk': self.vocab_entry.id}
            ),
            data=json.dumps(vocab_entry_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated
        self.login_test_user(self.user.username)

        response = self.client.put(
            reverse(
                'api:vocab-entry-detail',
                kwargs={'pk': self.vocab_entry.id}
            ),
            data=json.dumps(vocab_entry_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_permissions_delete(self):
        # Not authenticated
        self.client.logout()

        response = self.client.delete(
            reverse('api:vocab-entry-detail', kwargs={'pk': self.vocab_entry.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated
        self.login_test_user(self.user.username)

        response = self.client.delete(
            reverse('api:vocab-entry-detail', kwargs={'pk': self.vocab_entry.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_204_NO_CONTENT)


class VocabEntryImportViewTest(TestCommon):

    def test_inheritance(self):
        classes = (
            APIDefaultsMixin,
            APIView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntryImportView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse('api:vocab_entries_import'))
        self.assertEqual(
            found.func.__name__,
            VocabEntryImportView.as_view().__name__
        )

    def test_view_setup(self):
        view = VocabEntryImportView()
        permission_classes = [IsAuthenticated, IsSuperuser]

        self.assertEqual(permission_classes, view.permission_classes)

    def test_view_imports_vocab_entries_json(self):
        request = self.get_dummy_request()
        self.login_test_user(self.superuser.username)
        vocab_entry_data = {
            'entry': 'spacecraft',
            'description': 'A space vehicle',
            'language': 'en',
            'date_created': '2018-04-12T16:49:54.154036'
        }
        VocabEntry.objects.create(
            entry=vocab_entry_data['entry'],
            language=vocab_entry_data['language'],
            description=vocab_entry_data['description'],
            date_created=vocab_entry_data['date_created']
        )
        data = export_vocab_entries(request=request)
        VocabEntry.objects.all().delete()
        self.assertFalse(
            VocabEntry.objects.filter(
                language=vocab_entry_data['language'],
                entry=vocab_entry_data['entry'],
                description=vocab_entry_data['description'],
                date_created=vocab_entry_data['date_created']
            ).exists()
        )
        self.client.post(
            reverse('api:vocab_entries_import'),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertTrue(
            VocabEntry.objects.filter(
                language=vocab_entry_data['language'],
                entry=vocab_entry_data['entry'],
                description=vocab_entry_data['description'],
                date_created=vocab_entry_data['date_created']
            ).exists()
        )

        # Permissions
    def test_permissions_import(self):
        request = self.get_dummy_request()
        vocab_entry_data = {
            'entry': 'spacecraft',
            'description': 'A space vehicle',
            'language': 'en',
            'date_created': '2018-04-12T16:49:54.154036'
        }
        VocabEntry.objects.create(
            entry=vocab_entry_data['entry'],
            language=vocab_entry_data['language'],
            description=vocab_entry_data['description'],
            date_created=vocab_entry_data['date_created']
        )
        data = export_vocab_entries(request=request)

        # Not authenticated
        response = self.client.post(
            reverse('api:vocab_entries_import'),
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated non superuser
        self.login_test_user(self.user.username)

        response = self.client.post(
            reverse('api:vocab_entries_import'),
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Superuser
        self.login_test_user(self.superuser.username)

        response = self.client.post(
            reverse('api:vocab_entries_import'),
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, drf_status.HTTP_201_CREATED)


class VocabEntryExportViewTest(TestCommon):

    def test_inheritance(self):
        classes = (
            APIDefaultsMixin,
            APIView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntryExportView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse('api:vocab_entries_export'))
        self.assertEqual(
            found.func.__name__,
            VocabEntryExportView.as_view().__name__
        )

    def test_view_setup(self):
        view = VocabEntryExportView()
        permission_classes = [IsAuthenticated, IsSuperuser]

        self.assertEqual(permission_classes, view.permission_classes)

    def test_view_exports_vocab_entries_json(self):
        self.login_test_user(username=self.superuser.username)

        request = self.get_dummy_request()
        VocabEntry.objects.create(
            entry='entry one',
            language='en'
        )
        VocabEntry.objects.create(
            entry='entry two',
            language='es'
        )
        response = self.client.get(reverse(
            'api:vocab_entries_export'
        ))
        expected_data = export_vocab_entries(request=request)
        data = response.data

        self.assertEqual(len(data['vocab_entries']), 2)
        self.assertEqual(expected_data, response.data)

    def test_permissions_export(self):
        # Not authenticated
        self.client.logout()

        response = self.client.get(reverse(
            'api:vocab_entries_export'
        ))

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated non-superuser
        self.login_test_user(self.user.username)

        response = self.client.get(reverse(
            'api:vocab_entries_export'
        ))

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Superuser
        self.login_test_user(self.superuser.username)

        response = self.client.get(reverse(
            'api:vocab_entries_export'
        ))

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)


class VocabEntryLanguageExportViewTest(TestCommon):

    def setUp(self):
        super(VocabEntryLanguageExportViewTest, self).setUp()

    def test_inheritance(self):
        classes = (
            VocabEntryExportView,
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntryLanguageExportView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                'api:vocab_entries_language_export',
                kwargs={'language': 'en'}
            )
        )
        self.assertEqual(
            found.func.__name__,
            VocabEntryLanguageExportView.as_view().__name__
        )

    def test_view_exports_vocab_entries_json(self):
        self.login_test_user(username=self.superuser.username)

        request = self.get_dummy_request()
        VocabEntry.objects.create(
            entry='entry one',
            language='en'
        )
        VocabEntry.objects.create(
            entry='entry two',
            language='en'
        )
        VocabEntry.objects.create(
            entry='entry three',
            language='es'
        )
        response = self.client.get(
            reverse(
                'api:vocab_entries_language_export',
                kwargs={'language': 'es'}
            )
        )
        expected_data = export_vocab_entries(request=request, language='es')
        data = response.data
        self.assertEqual(len(data['vocab_entries']), 1)
        self.assertEqual(expected_data, response.data)


class VocabSourceExportViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceExportViewTest, self).setUp()
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='Test source',
            source_type=VocabSource.BOOK
        )

    def test_inheritance(self):
        classes = (
            APIDefaultsMixin,
            APIView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceExportView, class_name))

    def test_correct_view_used(self):
        found = resolve(
            reverse(
                'api:vocab_source_export',
                kwargs={'vocab_source_pk': self.vocab_source.id}
            )
        )
        self.assertEqual(
            found.func.__name__,
            VocabSourceExportView.as_view().__name__
        )

    def test_view_setup(self):
        view = VocabSourceExportView()
        permission_classes = [IsAuthenticated, CreatorPermission]

        self.assertEqual(permission_classes, view.permission_classes)


# class VocabSourceImportViewTest(TestCommon):

#     def setUp(self):
#         super(VocabSourceImportViewTest, self).setUp()
#         self.vocab_project = VocabProject.objects.create(
#             owner=self.user,
#             name='test project'
#         )
#         vocab_source = VocabSource.objects.create(
#             vocab_project=self.vocab_project,
#             creator=self.user,
#             name='Test source',
#             source_type=VocabSource.BOOK
#         )
#         request = self.request_factory.get('/fake-path')
#         self.vocab_source_data = export_vocab_source(request, vocab_source)
#         vocab_source.delete()

#     def test_inheritance(self):
#         classes = (
#             APIDefaultsMixin,
#             APIView
#         )
#         for class_name in classes:
#             self.assertTrue(issubclass(VocabSourceExportView, class_name))

#     def test_correct_view_used(self):
#         found = resolve(reverse('api:vocab_source_import'))
#         self.assertEqual(
#             found.func.__name__,
#             VocabSourceImportView.as_view().__name__
#         )

#     def test_view_imports_vocab_source_json(self):
#         self.login_test_user(self.user.username)
#         self.assertFalse(
#             VocabSource.objects.filter(
#                 creator_id=self.user.id,
#                 name=self.vocab_source_data['vocab_source_data']['name']
#             ).exists()
#         )
#         self.client.post(
#             reverse('api:vocab_source_import'),
#             json.dumps(self.vocab_source_data),
#             content_type='application/json'
#         )
#         self.assertTrue(
#             VocabSource.objects.filter(
#                 creator_id=self.user.id,
#                 name=self.vocab_source_data['vocab_source_data']['name']
#             ).exists()
#         )


# class VocabContextViewSetTest(TestCommon):

#     def setUp(self):
#         super(VocabContextViewSetTest, self).setUp()
#         self.vocab_project = VocabProject.objects.create(
#             owner=self.user,
#             name='test project'
#         )
#         self.vocab_source = VocabSource.objects.create(
#             vocab_project=self.vocab_project,
#             creator=self.user,
#             name='test source'
#         )
#         self.vocab_context = VocabContext.objects.create(
#             vocab_source=self.vocab_source,
#             content='This is some content.'
#         )

#     def get_context_serializer_data(self, vocab_context):
#         serializer = VocabContextSerializer(
#             vocab_context,
#             context={'request': self.get_dummy_request()}
#         )
#         return json.loads(serializer.json_data())

#     def test_view_setup(self):
#         view = VocabContextViewSet()
#         self.assertEqual('pk', view.lookup_field)
#         self.assertEqual('pk', view.lookup_url_kwarg)
#         self.assertEqual(VocabContextSerializer, view.serializer_class)
#         self.assertCountEqual(
#             VocabContext.objects.select_related('vocab_source'),
#             view.queryset
#         )

#     def test_inheritance(self):
#         classes = (
#             APIDefaultsMixin,
#             RetrieveModelMixin,
#             UpdateModelMixin,
#             DestroyModelMixin,
#             ListModelMixin,
#             GenericViewSet
#         )
#         for class_name in classes:
#             self.assertTrue(issubclass(VocabContextViewSet, class_name))

#     def test_view_detail(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(
#             reverse(
#                 'api:vocab-context-detail',
#                 kwargs={'pk': self.vocab_context.id}
#             ),
#         )
#         data = self.get_context_serializer_data(self.vocab_context)
#         self.assertEqual(
#             data,
#             json.loads(response.content)
#         )

#     def test_view_list(self):
#         self.login_test_user(self.user.username)
#         vocab_source_2 = VocabSource.objects.create(
#             vocab_project=self.vocab_project,
#             creator=self.user,
#             name='test source 2'
#         )
#         vocab_context_2 = VocabContext.objects.create(
#             vocab_source=vocab_source_2,
#             content='context 2'
#         )
#         data_1 = self.get_context_serializer_data(self.vocab_context)
#         data_2 = self.get_context_serializer_data(vocab_context_2)
#         response = self.client.get(
#             reverse('api:vocab-context-list')
#         )
#         self.assertCountEqual([data_1, data_2], json.loads(response.content))

#     def test_view_update(self):
#         self.login_test_user(self.user.username)

#         vocab_context_data = {'content': 'some content'}
#         self.assertNotEqual(
#             self.vocab_context.content,
#             vocab_context_data['content']
#         )
#         response = self.client.put(
#             reverse(
#                 'api:vocab-context-detail',
#                 kwargs={'pk': self.vocab_context.id}
#             ),
#             data=json.dumps(vocab_context_data),
#             content_type='application/json'
#         )
#         self.vocab_context.refresh_from_db()
#         self.assertEqual(response.status_code, drf_status.HTTP_200_OK)
#         self.assertEqual(
#             self.vocab_context.content,
#             vocab_context_data['content']
#         )

#     def test_view_delete(self):
#         self.login_test_user(self.user.username)
#         id = self.vocab_context.id
#         self.assertTrue(VocabContext.objects.filter(id=id).exists())
#         self.client.delete(
#             reverse('api:vocab-context-detail', kwargs={'pk': self.vocab_context.id})
#         )
#         self.assertFalse(VocabContext.objects.filter(id=id).exists())

#     def test_add_vocab_entry(self):
#         self.login_test_user(self.user.username)
#         vocab_entry = VocabEntry.objects.create(
#             language='es',
#             entry='tergiversar'
#         )
#         vocab_entry_data = {'vocab_entry_id': vocab_entry.id}
#         self.assertFalse(
#             VocabContextEntry.objects.filter(
#                 vocab_context_id=self.vocab_context.id,
#                 vocab_entry_id=vocab_entry.id
#             ).exists()
#         )
#         self.client.post(
#             reverse(
#                 'api:vocab-context-add-vocab-entry',
#                 kwargs={'pk': self.vocab_context.id}
#             ),
#             data=vocab_entry_data
#         )
#         self.assertTrue(
#             VocabContextEntry.objects.filter(
#                 vocab_context_id=self.vocab_context.id,
#                 vocab_entry_id=vocab_entry.id
#             ).exists()
#         )

#     def test_add_vocab_entry_tag(self):
#         self.login_test_user(self.user.username)
#         vocab_entry = VocabEntry.objects.create(
#             language='es',
#             entry='tergiversar'
#         )
#         tag = 'tergiversa'
#         data = {
#             'vocab_entry_id': vocab_entry.id,
#             'vocab_entry_tag': tag
#         }
#         VocabContextEntry.objects.create(
#             vocab_context_id=self.vocab_context.id,
#             vocab_entry_id=vocab_entry.id
#         )
#         self.client.post(
#             reverse(
#                 'api:vocab-context-add-vocab-entry-tag',
#                 kwargs={'pk': self.vocab_context.id}
#             ),
#             data=data
#         )
#         vocab_context_entry = VocabContextEntry.objects.get(
#             vocab_context_id=self.vocab_context.id,
#             vocab_entry_id=vocab_entry.id
#         )
#         tags = vocab_context_entry.get_vocab_entry_tags()
#         self.assertIn(tag, tags)

#     def test_remove_vocab_entry(self):
#         self.login_test_user(self.user.username)
#         vocab_entry = VocabEntry.objects.create(
#             language='es',
#             entry='tergiversar'
#         )
#         data = {
#             'vocab_entry_id': vocab_entry.id,
#         }
#         VocabContextEntry.objects.create(
#             vocab_context_id=self.vocab_context.id,
#             vocab_entry_id=vocab_entry.id
#         )
#         self.client.post(
#             reverse(
#                 'api:vocab-context-remove-vocab-entry',
#                 kwargs={'pk': self.vocab_context.id}
#             ),
#             data=data
#         )
#         self.assertFalse(
#             VocabContextEntry.objects.filter(
#                 vocab_context_id=self.vocab_context.id,
#                 vocab_entry_id=vocab_entry.id
#             ).exists()
#         )

#     def test_remove_vocab_entry_tag(self):
#         self.login_test_user(self.user.username)
#         vocab_entry = VocabEntry.objects.create(
#             language='es',
#             entry='tergiversar'
#         )
#         tag = 'tergiversa'
#         data = {
#             'vocab_entry_id': vocab_entry.id,
#             'vocab_entry_tag': tag
#         }
#         vocab_context_entry = VocabContextEntry.objects.create(
#             vocab_context_id=self.vocab_context.id,
#             vocab_entry_id=vocab_entry.id
#         )
#         vocab_context_entry.add_vocab_entry_tag(tag)

#         tags = vocab_context_entry.get_vocab_entry_tags()
#         self.assertIn(tag, tags)

#         self.client.post(
#             reverse(
#                 'api:vocab-context-remove-vocab-entry-tag',
#                 kwargs={'pk': self.vocab_context.id}
#             ),
#             data=data
#         )

#         tags = vocab_context_entry.get_vocab_entry_tags()
#         self.assertNotIn(tag, tags)


# class NestedVocabContextViewSetTest(TestCommon):

#     def setUp(self):
#         super(NestedVocabContextViewSetTest, self).setUp()
#         self.vocab_project = VocabProject.objects.create(
#             owner=self.user,
#             name='test project'
#         )
#         self.vocab_source = VocabSource.objects.create(
#             vocab_project=self.vocab_project,
#             creator=self.user,
#             name='test source 1'
#         )
#         self.vocab_source_2 = VocabSource.objects.create(
#             vocab_project=self.vocab_project,
#             creator=self.user,
#             name='test source 2'
#         )
#         self.vocab_context_1 = VocabContext.objects.create(
#             vocab_source=self.vocab_source,
#             content='test content 1'
#         )
#         self.vocab_context_2 = VocabContext.objects.create(
#             vocab_source=self.vocab_source,
#             content='test content 2'
#         )
#         self.vocab_context_3 = VocabContext.objects.create(
#             vocab_source=self.vocab_source_2,
#             content='test content 3'
#         )
#         self.vocab_context_4 = VocabContext.objects.create(
#             vocab_source=self.vocab_source_2,
#             content='test content 4'
#         )

#     def get_context_serializer_data(self, vocab_context):
#         serializer = VocabContextSerializer(
#             vocab_context,
#             context={'request': self.get_dummy_request()}
#         )
#         return json.loads(serializer.json_data())

#     def test_view_setup(self):
#         view = NestedVocabContextViewSet()
#         self.assertEqual('pk', view.lookup_field)
#         self.assertEqual('pk', view.lookup_url_kwarg)
#         self.assertEqual(VocabContextSerializer, view.serializer_class)
#         self.assertCountEqual(
#             VocabContext.objects.select_related('vocab_source'),
#             view.queryset
#         )

#     def test_inheritance(self):
#         classes = (
#             APIDefaultsMixin,
#             BatchMixin,
#             CreateModelMixin,
#             ListModelMixin,
#             GenericViewSet
#         )
#         for class_name in classes:
#             self.assertTrue(
#                 issubclass(NestedVocabContextViewSet, class_name)
#             )

#     def test_view_create(self):
#         vocab_context_data = {
#             'content': 'test content'
#         }
#         self.assertFalse(
#             VocabContext.objects.filter(
#                 vocab_source=self.vocab_source,
#                 content=vocab_context_data['content']
#             ).exists()
#         )
#         self.login_test_user(self.user.username)
#         self.client.post(
#             reverse(
#                 'api:nested-vocab-context-list',
#                 kwargs={'vocab_source_pk': self.vocab_source.id}
#             ),
#             data=vocab_context_data
#         )
#         self.assertTrue(
#             VocabContext.objects.filter(
#                 vocab_source=self.vocab_source,
#                 content=vocab_context_data['content']
#             ).exists()
#         )

#     def test_view_list(self):
#         self.login_test_user(self.user.username)

#         # Source 1
#         data_1 = self.get_context_serializer_data(self.vocab_context_1)
#         data_2 = self.get_context_serializer_data(self.vocab_context_2)
#         response = self.client.get(
#             reverse(
#                 'api:nested-vocab-context-list',
#                 kwargs={'vocab_source_pk': self.vocab_source.id}
#             )
#         )
#         self.assertCountEqual([data_1, data_2], json.loads(response.content))

#         # Source 2
#         data_3 = self.get_context_serializer_data(self.vocab_context_3)
#         data_4 = self.get_context_serializer_data(self.vocab_context_4)
#         response = self.client.get(
#             reverse(
#                 'api:nested-vocab-context-list',
#                 kwargs={'vocab_source_pk': self.vocab_source_2.id}
#             )
#         )
#         self.assertCountEqual([data_3, data_4], json.loads(response.content))


# class VocabContextEntryViewSetTest(TestCommon):

#     def setUp(self):
#         super(VocabContextEntryViewSetTest, self).setUp()
#         self.vocab_project = VocabProject.objects.create(
#             owner=self.user,
#             name='test project'
#         )
#         self.vocab_source = VocabSource.objects.create(
#             vocab_project=self.vocab_project,
#             creator=self.user,
#             name='test source'
#         )
#         self.vocab_context = VocabContext.objects.create(
#             vocab_source=self.vocab_source,
#             content='This is some content.'
#         )
#         self.vocab_entry = VocabEntry.objects.create(
#             language='es',
#             entry='tergiversar'
#         )
#         self.vocab_context_entry = VocabContextEntry.objects.create(
#             vocab_context_id=self.vocab_context.id,
#             vocab_entry_id=self.vocab_entry.id
#         )

#     def get_context_entry_serializer_data(self, vocab_context_entry):
#         serializer = VocabContextEntrySerializer(
#             vocab_context_entry,
#             context={'request': self.get_dummy_request()}
#         )
#         return json.loads(serializer.json_data())

#     def test_view_setup(self):
#         view = VocabContextEntryViewSet()
#         self.assertEqual('pk', view.lookup_field)
#         self.assertEqual('pk', view.lookup_url_kwarg)
#         self.assertEqual(VocabContextEntrySerializer, view.serializer_class)
#         self.assertCountEqual(
#             VocabContextEntry.objects.select_related('vocab_entry', 'vocab_context').prefetch_related('vocab_entry_tags'),
#             view.queryset
#         )

#     def test_inheritance(self):
#         classes = (
#             APIDefaultsMixin,
#             RetrieveModelMixin,
#             DestroyModelMixin,
#             ListModelMixin,
#             GenericViewSet
#         )
#         for class_name in classes:
#             self.assertTrue(
#                 issubclass(VocabContextEntryViewSet, class_name)
#             )

#     def test_view_detail(self):
#         self.login_test_user(self.user.username)
#         response = self.client.get(
#             reverse(
#                 'api:vocab-context-entry-detail',
#                 kwargs={'pk': self.vocab_context_entry.id}
#             ),
#         )
#         data = self.get_context_entry_serializer_data(self.vocab_context_entry)
#         self.assertEqual(
#             data,
#             json.loads(response.content)
#         )

#     def test_view_delete(self):
#         self.login_test_user(self.user.username)
#         data = {
#             'vocab_entry_id': self.vocab_context_entry.vocab_entry_id,
#             'vocab_context_id': self.vocab_context_entry.vocab_context_id
#         }
#         self.assertTrue(
#             VocabContextEntry.objects.filter(
#                 vocab_entry_id=data['vocab_entry_id'],
#                 vocab_context_id=data['vocab_context_id']
#             ).exists()
#         )
#         self.client.delete(
#             reverse(
#                 'api:vocab-context-entry-detail',
#                 kwargs={'pk': self.vocab_context_entry.id}
#             )
#         )
#         self.assertFalse(
#             VocabContextEntry.objects.filter(
#                 vocab_entry_id=data['vocab_entry_id'],
#                 vocab_context_id=data['vocab_context_id']
#             ).exists()
#         )


# class NestedVocabContextEntryViewSetTest(TestCommon):

#     def setUp(self):
#         super(NestedVocabContextEntryViewSetTest, self).setUp()
#         self.vocab_project = VocabProject.objects.create(
#             owner=self.user,
#             name='test project'
#         )
#         self.vocab_source = VocabSource.objects.create(
#             vocab_project=self.vocab_project,
#             creator=self.user,
#             name='test source'
#         )
#         self.vocab_context = VocabContext.objects.create(
#             vocab_source=self.vocab_source,
#             content='This is some content.'
#         )
