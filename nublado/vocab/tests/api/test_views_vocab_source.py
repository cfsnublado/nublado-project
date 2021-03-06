import json

from django.contrib.auth import get_user_model
from django.urls import resolve, reverse

from rest_framework import status as drf_status
from rest_framework.mixins import (
    DestroyModelMixin, ListModelMixin,
    RetrieveModelMixin, UpdateModelMixin
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from core.api.views_api import APIDefaultsMixin
from vocab.api.pagination import SmallPagination
from vocab.api.permissions import SourceCreatorPermission, ReadPermission
from vocab.api.views_vocab_source import (
    VocabSourceExportView, VocabSourceViewSet
)
from vocab.models import VocabSource
from vocab.serializers import VocabSourceSerializer
from .base_test import TestCommon

User = get_user_model()


class VocabSourceViewSetTest(TestCommon):

    def setUp(self):
        super(VocabSourceViewSetTest, self).setUp()

        self.vocab_source = VocabSource.objects.create(
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
        self.assertEqual(SmallPagination, view.pagination_class)

        qs = VocabSource.objects.prefetch_related('vocab_contexts')
        self.assertCountEqual(
            qs, view.queryset
        )
        self.assertEqual(str(qs.query), str(view.queryset.query))

        permission_classes = [ReadPermission, SourceCreatorPermission]

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
        vocab_source_2 = VocabSource.objects.create(
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
    def test_permissions_detail(self):
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

        # Authenticated not creator
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

        # Superuser not creator
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

        # Authenticated not creator
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

        # Superuser not creator
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name='test source'
        )

        self.client.logout()
        self.login_test_user(self.superuser.username)

        response = self.client.delete(
            reverse('api:vocab-source-detail', kwargs={'pk': self.vocab_source.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_204_NO_CONTENT)


class VocabSourceExportViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceExportViewTest, self).setUp()

        self.vocab_source = VocabSource.objects.create(
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
        permission_classes = [IsAuthenticated, SourceCreatorPermission]

        self.assertEqual(permission_classes, view.permission_classes)


# class VocabSourceImportViewTest(TestCommon):

#     def setUp(self):
#         super(VocabSourceImportViewTest, self).setUp()

#         vocab_source = VocabSource.objects.create(
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
