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

from core.utils import setup_test_view
from ..api.permissions import CreatorPermission, IsSuperuser
from ..api.views_api import (
    APIDefaultsMixin, BatchMixin, NestedVocabContextViewSet,
    NestedVocabSourceViewSet, VocabContextViewSet, VocabContextEntryViewSet,
    VocabEntryImportView, VocabEntryExportView, VocabEntryViewSet,
    VocabEntryLanguageExportView, VocabProjectViewSet, VocabSourceExportView,
    VocabSourceImportView, VocabSourceViewSet
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
        self.user = User.objects.create_superuser(
            username='cfs',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@foo.com',
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

    def get_project_serializer_data(self, project):
        serializer = VocabProjectSerializer(
            project,
            context={'request': self.get_dummy_request()}
        )
        return json.loads(serializer.json_data())

    def test_view_setup(self):
        view = VocabProjectViewSet()
        permission_classes = (IsAuthenticated,)
        self.assertEqual(permission_classes, view.permission_classes)
        self.assertEqual('pk', view.lookup_field)
        self.assertEqual('pk', view.lookup_url_kwarg)
        self.assertEqual(VocabProjectSerializer, view.serializer_class)
        self.assertCountEqual(VocabProject.objects.all(), view.queryset)

    def test_view_permissions(self):
        response = self.client.get(
            reverse(
                'api:vocab-project-detail',
                kwargs={'pk': self.vocab_project.id}
            ),
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'api:vocab-project-detail',
                kwargs={'pk': self.vocab_project.id}
            ),
        )
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_inheritance(self):
        classes = (
            APIDefaultsMixin,
            ModelViewSet
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabProjectViewSet, class_name))

    def test_view_create(self):
        self.login_test_user(self.user.username)
        vocab_project_data = {
            'name': 'another test project',
            'description': 'another test project'
        }
        self.assertFalse(
            VocabProject.objects.filter(name=vocab_project_data['name']).exists()
        )
        self.client.post(
            reverse('api:vocab-project-list'),
            data=vocab_project_data
        )
        self.assertTrue(
            VocabProject.objects.filter(
                owner=self.user,
                name=vocab_project_data['name']
            ).exists()
        )

    def test_view_detail(self):
        self.login_test_user(self.user.username)
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
        self.login_test_user(self.user.username)
        vocab_project_2 = VocabProject.objects.create(
            owner=self.user,
            name='test project 2'
        )
        data_1 = self.get_project_serializer_data(self.vocab_project)
        data_2 = self.get_project_serializer_data(vocab_project_2)
        response = self.client.get(
            reverse('api:vocab-project-list')
        )
        self.assertCountEqual([data_1, data_2], json.loads(response.content))

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
        permission_classes = (IsAuthenticated,)
        self.assertEqual(permission_classes, view.permission_classes)
        self.assertEqual('pk', view.lookup_field)
        self.assertEqual('pk', view.lookup_url_kwarg)
        self.assertEqual(VocabEntrySerializer, view.serializer_class)
        self.assertCountEqual(VocabEntry.objects.all(), view.queryset)

    def test_view_permissions(self):
        response = self.client.get(
            reverse(
                'api:vocab-entry-detail',
                kwargs={'pk': self.vocab_entry.id}
            ),
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'api:vocab-entry-detail',
                kwargs={'pk': self.vocab_entry.id}
            ),
        )
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

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
        self.login_test_user(self.user.username)
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
        self.login_test_user(self.user.username)
        vocab_entry_2 = VocabEntry.objects.create(
            language='es',
            entry='hola'
        )
        data_1 = self.get_entry_serializer_data(self.vocab_entry)
        data_2 = self.get_entry_serializer_data(vocab_entry_2)
        response = self.client.get(
            reverse('api:vocab-entry-list')
        )
        self.assertCountEqual([data_1, data_2], json.loads(response.content))

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
        self.login_test_user(self.user.username)
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
        request = self.get_dummy_request()
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
        request = self.get_dummy_request()
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

    def get_source_serializer_data(self, source):
        serializer = VocabSourceSerializer(
            source,
            context={'request': self.get_dummy_request()}
        )
        return json.loads(serializer.json_data())

    def test_view_setup(self):
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


class NestedVocabSourceViewSetTest(TestCommon):

    def setUp(self):
        super(NestedVocabSourceViewSetTest, self).setUp()
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
        permission_classes = (IsAuthenticated,)
        self.assertEqual(permission_classes, view.permission_classes)
        self.assertEqual('pk', view.lookup_field)
        self.assertEqual('pk', view.lookup_url_kwarg)
        self.assertEqual(VocabSourceSerializer, view.serializer_class)
        self.assertIsNone(view.vocab_project)
        self.assertCountEqual(VocabSource.objects.prefetch_related('vocab_contexts'), view.queryset)

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
        vocab_source_data = {
            'name': 'another test source'
        }
        self.assertFalse(
            VocabSource.objects.filter(
                name=vocab_source_data['name']
            ).exists()
        )
        self.login_test_user(self.user.username)
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
        self.login_test_user(self.user.username)

        # Project 1
        data_1 = self.get_source_serializer_data(self.vocab_source_1)
        data_2 = self.get_source_serializer_data(self.vocab_source_2)
        response = self.client.get(
            reverse(
                'api:nested-vocab-source-list',
                kwargs={'vocab_project_pk': self.vocab_project.id}
            )
        )
        self.assertCountEqual([data_1, data_2], json.loads(response.content))

        # Project 2
        data_3 = self.get_source_serializer_data(self.vocab_source_3)
        data_4 = self.get_source_serializer_data(self.vocab_source_4)
        response = self.client.get(
            reverse(
                'api:nested-vocab-source-list',
                kwargs={'vocab_project_pk': self.vocab_project_2.id}
            )
        )
        self.assertCountEqual([data_3, data_4], json.loads(response.content))


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

    def test_view_permission_classes(self):
        request = self.get_dummy_request()
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
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
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


class VocabContextViewSetTest(TestCommon):

    def setUp(self):
        super(VocabContextViewSetTest, self).setUp()
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source'
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='This is some content.'
        )

    def get_context_serializer_data(self, vocab_context):
        serializer = VocabContextSerializer(
            vocab_context,
            context={'request': self.get_dummy_request()}
        )
        return json.loads(serializer.json_data())

    def test_view_setup(self):
        view = VocabContextViewSet()
        permission_classes = (IsAuthenticated,)
        self.assertEqual(permission_classes, view.permission_classes)
        self.assertEqual('pk', view.lookup_field)
        self.assertEqual('pk', view.lookup_url_kwarg)
        self.assertEqual(VocabContextSerializer, view.serializer_class)
        self.assertCountEqual(
            VocabContext.objects.select_related('vocab_source'),
            view.queryset
        )

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
            self.assertTrue(issubclass(VocabContextViewSet, class_name))

    def test_view_detail(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'api:vocab-context-detail',
                kwargs={'pk': self.vocab_context.id}
            ),
        )
        data = self.get_context_serializer_data(self.vocab_context)
        self.assertEqual(
            data,
            json.loads(response.content)
        )

    def test_view_list(self):
        self.login_test_user(self.user.username)
        vocab_source_2 = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source 2'
        )
        vocab_context_2 = VocabContext.objects.create(
            vocab_source=vocab_source_2,
            content='context 2'
        )
        data_1 = self.get_context_serializer_data(self.vocab_context)
        data_2 = self.get_context_serializer_data(vocab_context_2)
        response = self.client.get(
            reverse('api:vocab-context-list')
        )
        self.assertCountEqual([data_1, data_2], json.loads(response.content))

    def test_view_update(self):
        self.login_test_user(self.user.username)

        vocab_context_data = {'content': 'some content'}
        self.assertNotEqual(
            self.vocab_context.content,
            vocab_context_data['content']
        )
        response = self.client.put(
            reverse(
                'api:vocab-context-detail',
                kwargs={'pk': self.vocab_context.id}
            ),
            data=json.dumps(vocab_context_data),
            content_type='application/json'
        )
        self.vocab_context.refresh_from_db()
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)
        self.assertEqual(
            self.vocab_context.content,
            vocab_context_data['content']
        )

    def test_view_delete(self):
        self.login_test_user(self.user.username)
        id = self.vocab_context.id
        self.assertTrue(VocabContext.objects.filter(id=id).exists())
        self.client.delete(
            reverse('api:vocab-context-detail', kwargs={'pk': self.vocab_context.id})
        )
        self.assertFalse(VocabContext.objects.filter(id=id).exists())

    def test_add_vocab_entry(self):
        self.login_test_user(self.user.username)
        vocab_entry = VocabEntry.objects.create(
            language='es',
            entry='tergiversar'
        )
        vocab_entry_data = {'vocab_entry_id': vocab_entry.id}
        self.assertFalse(
            VocabContextEntry.objects.filter(
                vocab_context_id=self.vocab_context.id,
                vocab_entry_id=vocab_entry.id
            ).exists()
        )
        self.client.post(
            reverse(
                'api:vocab-context-add-vocab-entry',
                kwargs={'pk': self.vocab_context.id}
            ),
            data=vocab_entry_data
        )
        self.assertTrue(
            VocabContextEntry.objects.filter(
                vocab_context_id=self.vocab_context.id,
                vocab_entry_id=vocab_entry.id
            ).exists()
        )

    def test_add_vocab_entry_tag(self):
        self.login_test_user(self.user.username)
        vocab_entry = VocabEntry.objects.create(
            language='es',
            entry='tergiversar'
        )
        tag = 'tergiversa'
        data = {
            'vocab_entry_id': vocab_entry.id,
            'vocab_entry_tag': tag
        }
        VocabContextEntry.objects.create(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=vocab_entry.id
        )
        self.client.post(
            reverse(
                'api:vocab-context-add-vocab-entry-tag',
                kwargs={'pk': self.vocab_context.id}
            ),
            data=data
        )
        vocab_context_entry = VocabContextEntry.objects.get(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=vocab_entry.id
        )
        tags = vocab_context_entry.get_vocab_entry_tags()
        self.assertIn(tag, tags)

    def test_remove_vocab_entry(self):
        self.login_test_user(self.user.username)
        vocab_entry = VocabEntry.objects.create(
            language='es',
            entry='tergiversar'
        )
        data = {
            'vocab_entry_id': vocab_entry.id,
        }
        VocabContextEntry.objects.create(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=vocab_entry.id
        )
        self.client.post(
            reverse(
                'api:vocab-context-remove-vocab-entry',
                kwargs={'pk': self.vocab_context.id}
            ),
            data=data
        )
        self.assertFalse(
            VocabContextEntry.objects.filter(
                vocab_context_id=self.vocab_context.id,
                vocab_entry_id=vocab_entry.id
            ).exists()
        )

    def test_remove_vocab_entry_tag(self):
        self.login_test_user(self.user.username)
        vocab_entry = VocabEntry.objects.create(
            language='es',
            entry='tergiversar'
        )
        tag = 'tergiversa'
        data = {
            'vocab_entry_id': vocab_entry.id,
            'vocab_entry_tag': tag
        }
        vocab_context_entry = VocabContextEntry.objects.create(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=vocab_entry.id
        )
        vocab_context_entry.add_vocab_entry_tag(tag)

        tags = vocab_context_entry.get_vocab_entry_tags()
        self.assertIn(tag, tags)

        self.client.post(
            reverse(
                'api:vocab-context-remove-vocab-entry-tag',
                kwargs={'pk': self.vocab_context.id}
            ),
            data=data
        )

        tags = vocab_context_entry.get_vocab_entry_tags()
        self.assertNotIn(tag, tags)


class NestedVocabContextViewSetTest(TestCommon):

    def setUp(self):
        super(NestedVocabContextViewSetTest, self).setUp()
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source 1'
        )
        self.vocab_source_2 = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source 2'
        )
        self.vocab_context_1 = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='test content 1'
        )
        self.vocab_context_2 = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='test content 2'
        )
        self.vocab_context_3 = VocabContext.objects.create(
            vocab_source=self.vocab_source_2,
            content='test content 3'
        )
        self.vocab_context_4 = VocabContext.objects.create(
            vocab_source=self.vocab_source_2,
            content='test content 4'
        )

    def get_context_serializer_data(self, vocab_context):
        serializer = VocabContextSerializer(
            vocab_context,
            context={'request': self.get_dummy_request()}
        )
        return json.loads(serializer.json_data())

    def test_view_setup(self):
        view = NestedVocabContextViewSet()
        permission_classes = (IsAuthenticated,)
        self.assertEqual(permission_classes, view.permission_classes)
        self.assertEqual('pk', view.lookup_field)
        self.assertEqual('pk', view.lookup_url_kwarg)
        self.assertEqual(VocabContextSerializer, view.serializer_class)
        self.assertCountEqual(
            VocabContext.objects.select_related('vocab_source'),
            view.queryset
        )

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
                issubclass(NestedVocabContextViewSet, class_name)
            )

    def test_view_create(self):
        vocab_context_data = {
            'content': 'test content'
        }
        self.assertFalse(
            VocabContext.objects.filter(
                vocab_source=self.vocab_source,
                content=vocab_context_data['content']
            ).exists()
        )
        self.login_test_user(self.user.username)
        self.client.post(
            reverse(
                'api:nested-vocab-context-list',
                kwargs={'vocab_source_pk': self.vocab_source.id}
            ),
            data=vocab_context_data
        )
        self.assertTrue(
            VocabContext.objects.filter(
                vocab_source=self.vocab_source,
                content=vocab_context_data['content']
            ).exists()
        )

    def test_view_list(self):
        self.login_test_user(self.user.username)

        # Source 1
        data_1 = self.get_context_serializer_data(self.vocab_context_1)
        data_2 = self.get_context_serializer_data(self.vocab_context_2)
        response = self.client.get(
            reverse(
                'api:nested-vocab-context-list',
                kwargs={'vocab_source_pk': self.vocab_source.id}
            )
        )
        self.assertCountEqual([data_1, data_2], json.loads(response.content))

        # Source 2
        data_3 = self.get_context_serializer_data(self.vocab_context_3)
        data_4 = self.get_context_serializer_data(self.vocab_context_4)
        response = self.client.get(
            reverse(
                'api:nested-vocab-context-list',
                kwargs={'vocab_source_pk': self.vocab_source_2.id}
            )
        )
        self.assertCountEqual([data_3, data_4], json.loads(response.content))


class VocabContextEntryViewSetTest(TestCommon):

    def setUp(self):
        super(VocabContextEntryViewSetTest, self).setUp()
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source'
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='This is some content.'
        )
        self.vocab_entry = VocabEntry.objects.create(
            language='es',
            entry='tergiversar'
        )
        self.vocab_context_entry = VocabContextEntry.objects.create(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=self.vocab_entry.id
        )

    def get_context_entry_serializer_data(self, vocab_context_entry):
        serializer = VocabContextEntrySerializer(
            vocab_context_entry,
            context={'request': self.get_dummy_request()}
        )
        return json.loads(serializer.json_data())

    def test_view_setup(self):
        view = VocabContextEntryViewSet()
        permission_classes = (IsAuthenticated,)
        self.assertEqual(permission_classes, view.permission_classes)
        self.assertEqual('pk', view.lookup_field)
        self.assertEqual('pk', view.lookup_url_kwarg)
        self.assertEqual(VocabContextEntrySerializer, view.serializer_class)
        self.assertCountEqual(
            VocabContextEntry.objects.select_related('vocab_entry', 'vocab_context').prefetch_related('vocab_entry_tags'),
            view.queryset
        )

    def test_inheritance(self):
        classes = (
            APIDefaultsMixin,
            RetrieveModelMixin,
            DestroyModelMixin,
            ListModelMixin,
            GenericViewSet
        )
        for class_name in classes:
            self.assertTrue(
                issubclass(VocabContextEntryViewSet, class_name)
            )

    def test_view_detail(self):
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                'api:vocab-context-entry-detail',
                kwargs={'pk': self.vocab_context_entry.id}
            ),
        )
        data = self.get_context_entry_serializer_data(self.vocab_context_entry)
        self.assertEqual(
            data,
            json.loads(response.content)
        )

    def test_view_delete(self):
        self.login_test_user(self.user.username)
        data = {
            'vocab_entry_id': self.vocab_context_entry.vocab_entry_id,
            'vocab_context_id': self.vocab_context_entry.vocab_context_id
        }
        self.assertTrue(
            VocabContextEntry.objects.filter(
                vocab_entry_id=data['vocab_entry_id'],
                vocab_context_id=data['vocab_context_id']
            ).exists()
        )
        self.client.delete(
            reverse(
                'api:vocab-context-entry-detail',
                kwargs={'pk': self.vocab_context_entry.id}
            )
        )
        self.assertFalse(
            VocabContextEntry.objects.filter(
                vocab_entry_id=data['vocab_entry_id'],
                vocab_context_id=data['vocab_context_id']
            ).exists()
        )


class NestedVocabContextEntryViewSetTest(TestCommon):

    def setUp(self):
        super(NestedVocabContextEntryViewSetTest, self).setUp()
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='test source'
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='This is some content.'
        )
