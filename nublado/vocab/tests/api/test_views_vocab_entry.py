import json

from django.contrib.auth import get_user_model
from django.urls import resolve, reverse

from rest_framework import status as drf_status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from core.api.views_api import APIDefaultsMixin
from vocab.api.pagination import LargePagination
from vocab.api.permissions import IsSuperuser, ReadWritePermission
from vocab.api.views_mixins import BatchMixin
from vocab.api.views_vocab_entry import (
    VocabEntryExportView, VocabEntryLanguageExportView,
    VocabEntryImportView, VocabEntryViewSet
)
from vocab.models import VocabEntry
from vocab.serializers import VocabEntrySerializer
from vocab.utils import export_vocab_entries
from .base_test import TestCommon

User = get_user_model()


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
