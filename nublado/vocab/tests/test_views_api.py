import json

from rest_framework import status as drf_status
from rest_framework.mixins import (
    DestroyModelMixin, ListModelMixin,
    RetrieveModelMixin, UpdateModelMixin
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from django.contrib.auth import get_user_model
from django.urls import resolve, reverse
from django.test import RequestFactory, TestCase

from core.utils import setup_test_view
from ..api.permissions import CreatorPermission, IsSuperuser
from ..api.views_api import (
    APIDefaultsMixin, VocabEntryImportView,
    VocabEntryExportView, VocabEntryLanguageExportView,
    VocabSourceExportView, VocabSourceImportView,
    VocabSourceViewSet
)
from ..conf import settings
from ..models import VocabEntry, VocabProject, VocabSource
from ..serializers import (
    VocabSourceSerializer
)
from ..utils import export_vocab_entries, export_vocab_source

User = get_user_model()

APP_NAME = 'vocab'
URL_PREFIX = getattr(settings, 'VOCAB_URL_PREFIX')


class TestCommon(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_superuser(
            username='cfs',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@foo.com',
            password=self.pwd
        )
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)


class VocabSourceViewSetTest(TestCommon):

    def setUp(self):
        super(VocabSourceViewSetTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source'
        )

    def get_dummy_request(self):
        request = self.request_factory.get('/fake-path')
        request.user = self.user
        return request

    def get_source_serializer_data(self, source):
        serializer = VocabSourceSerializer(
            source,
            context={'request': self.get_dummy_request()}
        )
        return json.loads(serializer.json_data())

    def test_view_setup(self):
        request = self.request_factory.get('/fake-path')
        request.user = self.user
        view = VocabSourceViewSet()
        permission_classes = (IsAuthenticated,)
        self.assertEqual(permission_classes, view.permission_classes)
        self.assertEqual('pk', view.lookup_field)
        self.assertEqual('pk', view.lookup_url_kwarg)
        self.assertEqual(VocabSourceSerializer, view.serializer_class)
        self.assertCountEqual(VocabSource.objects.prefetch_related('vocab_contexts'), view.queryset)

    def test_view_permissions(self):
        response = self.client.get(
            reverse(
                'api:vocab-source-detail',
                kwargs={'pk': self.vocab_source.id}
            ),
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'api:vocab-source-detail',
                kwargs={'pk': self.vocab_source.id}
            ),
        )
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

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
        self.login_test_user(self.user.username)
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
        self.login_test_user(self.user.username)
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
        response = self.client.get(
            reverse('api:vocab-source-list')
        )
        self.assertCountEqual([data_1, data_2], json.loads(response.content))

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

    def test_view_imports_vocab_entries_json(self):
        request = self.request_factory.get('/fake-path')
        request.user = self.user
        self.login_test_user(self.user.username)
        vocab_entry_data = {
            'creator': self.user,
            'entry': 'spacecraft',
            'description': 'A space vehicle',
            'language': 'en',
            'pronunciation_spelling': '**speys**-kraft',
            'pronunciation_ipa': '',
            'date_created': '2018-04-12T16:49:54.154036'
        }
        VocabEntry.objects.create(
            entry=vocab_entry_data['entry'],
            language=vocab_entry_data['language'],
            description=vocab_entry_data['description'],
            pronunciation_ipa=vocab_entry_data['pronunciation_ipa'],
            pronunciation_spelling=vocab_entry_data['pronunciation_spelling'],
            date_created=vocab_entry_data['date_created']
        )
        data = export_vocab_entries(request=request)
        VocabEntry.objects.all().delete()
        self.assertFalse(
            VocabEntry.objects.filter(
                language=vocab_entry_data['language'],
                entry=vocab_entry_data['entry'],
                pronunciation_ipa=vocab_entry_data['pronunciation_ipa'],
                pronunciation_spelling=vocab_entry_data['pronunciation_spelling'],
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
                pronunciation_ipa=vocab_entry_data['pronunciation_ipa'],
                pronunciation_spelling=vocab_entry_data['pronunciation_spelling'],
                description=vocab_entry_data['description'],
                date_created=vocab_entry_data['date_created']
            ).exists()
        )


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

    def test_view_permission_classes(self):
        request = self.request_factory.get('/fake-path')
        request.user = self.user
        view = setup_test_view(VocabEntryExportView(), request)
        response = view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)
        permission_classes = (IsAuthenticated, IsSuperuser)
        self.assertEqual(permission_classes, view.permission_classes)

    def test_view_permissions(self):
        user_2 = User.objects.create(
            username='kfl7',
            email='kfl7@foo.com',
            first_name='Karen',
            last_name='Fuentes',
            password=self.pwd
        )

        # Not authenticated
        response = self.client.get(
            reverse('api:vocab_entries_export')
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated
        self.login_test_user(user_2.username)
        response = self.client.get(
            reverse('api:vocab_entries_export')
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated superuser
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse('api:vocab_entries_export')
        )
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_view_exports_vocab_entries_json(self):
        self.login_test_user(username=self.user.username)
        request = self.request_factory.get('/fake-path')
        request.user = self.user
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

    def test_view_permissions(self):
        user_2 = User.objects.create(
            username='kfl7',
            email='kfl7@foo.com',
            first_name='Karen',
            last_name='Fuentes',
            password=self.pwd
        )

        # Non authenticated
        response = self.client.get(
            reverse(
                'api:vocab_entries_language_export',
                kwargs={'language': 'en'}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated
        self.login_test_user(user_2.username)
        response = self.client.get(
            reverse(
                'api:vocab_entries_language_export',
                kwargs={'language': 'en'}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated superuser
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'api:vocab_entries_language_export',
                kwargs={'language': 'en'}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_view_exports_vocab_entries_json(self):
        self.login_test_user(username=self.user.username)
        request = self.request_factory.get('/fake-path')
        request.user = self.user
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

    def test_view_permission_classes(self):
        request = self.request_factory.get('/fake-path')
        request.user = self.user
        view = setup_test_view(
            VocabSourceExportView(), request,
            vocab_source_pk=self.vocab_source.id
        )
        response = view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)
        permission_classes = (IsAuthenticated, CreatorPermission)
        self.assertEqual(permission_classes, view.permission_classes)

    def test_view_permissions(self):
        creator = User.objects.create(
            username='kfl7',
            email='kfl7@foo.com',
            first_name='Karen',
            last_name='Fuentes',
            password=self.pwd
        )
        non_creator = User.objects.create(
            username='foo7',
            email='foo7@foo.com',
            first_name='Foo',
            last_name='Foo',
            password=self.pwd
        )
        vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=creator,
            name='Another test source',
            source_type=VocabSource.BOOK
        )

        # Not authenticated
        response = self.client.get(
            reverse(
                'api:vocab_source_export',
                kwargs={'vocab_source_pk': vocab_source.id}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated non creator
        self.login_test_user(non_creator.username)
        response = self.client.get(
            reverse(
                'api:vocab_source_export',
                kwargs={'vocab_source_pk': vocab_source.id}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated creator
        self.login_test_user(creator.username)
        response = self.client.get(
            reverse(
                'api:vocab_source_export',
                kwargs={'vocab_source_pk': vocab_source.id}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

        # Authenticated non creator superuser
        self.login_test_user(self.user.username)
        self.assertTrue(self.user.is_superuser)
        response = self.client.get(
            reverse(
                'api:vocab_source_export',
                kwargs={'vocab_source_pk': vocab_source.id}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)


class VocabSourceImportViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceImportViewTest, self).setUp()
        vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='Test source',
            source_type=VocabSource.BOOK
        )
        request = self.request_factory.get('/fake-path')
        self.vocab_source_data = export_vocab_source(request, vocab_source)
        vocab_source.delete()

    def test_inheritance(self):
        classes = (
            APIDefaultsMixin,
            APIView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabSourceExportView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse('api:vocab_source_import'))
        self.assertEqual(
            found.func.__name__,
            VocabSourceImportView.as_view().__name__
        )

    def test_view_imports_vocab_source_json(self):
        self.login_test_user(self.user.username)
        self.assertFalse(
            VocabSource.objects.filter(
                creator_id=self.user.id,
                name=self.vocab_source_data['vocab_source_data']['name']
            ).exists()
        )
        self.client.post(
            reverse('api:vocab_source_import'),
            json.dumps(self.vocab_source_data),
            content_type='application/json'
        )
        self.assertTrue(
            VocabSource.objects.filter(
                creator_id=self.user.id,
                name=self.vocab_source_data['vocab_source_data']['name']
            ).exists()
        )
