import json

from rest_framework import status as drf_status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from django.contrib.auth import get_user_model
from django.urls import resolve, reverse
from django.test import RequestFactory, TestCase

from core.utils import setup_test_view
from ..api.permissions import CreatorPermission, IsSuperuser
from ..api.views_api import (
    APIDefaultsMixin, VocabEntryImportView,
    VocabEntryExportView, VocabEntryLanguageExportView,
    VocabSourceExportView, VocabSourceImportView
)
from ..conf import settings
from ..models import VocabEntry, VocabSource
from ..utils import export_vocab_entries, export_vocab_source

User = get_user_model()

APP_NAME = "vocab"
URL_PREFIX = getattr(settings, "VOCAB_URL_PREFIX")


class TestCommon(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.pwd = "Pizza?69p"
        self.user = User.objects.create_superuser(
            username="cfs",
            first_name="Christopher",
            last_name="Sanders",
            email="cfs7@foo.com",
            password=self.pwd
        )

    def login_test_user(self, username=None):
        self.client.login(username=username, password=self.pwd)


class VocabEntryImportViewTest(TestCommon):

    def test_inheritance(self):
        classes = (
            APIDefaultsMixin,
            APIView
        )
        for class_name in classes:
            self.assertTrue(issubclass(VocabEntryImportView, class_name))

    def test_correct_view_used(self):
        found = resolve(reverse("api:vocab_entries_import"))
        self.assertEqual(
            found.func.__name__,
            VocabEntryImportView.as_view().__name__
        )

    def test_view_imports_vocab_entries_json(self):
        request = self.request_factory.get("/fake-path")
        request.user = self.user
        self.login_test_user(self.user.username)
        vocab_entry_data = {
            "creator": self.user,
            "entry": "spacecraft",
            "description": "A space vehicle",
            "language": "en",
            "pronunciation_spelling": "**speys**-kraft",
            "pronunciation_ipa": "",
            "date_created": "2018-04-12T16:49:54.154036"
        }
        VocabEntry.objects.create(
            creator=self.user,
            entry=vocab_entry_data["entry"],
            language=vocab_entry_data["language"],
            description=vocab_entry_data["description"],
            pronunciation_ipa=vocab_entry_data["pronunciation_ipa"],
            pronunciation_spelling=vocab_entry_data["pronunciation_spelling"],
            date_created=vocab_entry_data["date_created"]
        )
        data = export_vocab_entries(request=request)
        VocabEntry.objects.all().delete()
        self.assertFalse(
            VocabEntry.objects.filter(
                language=vocab_entry_data["language"],
                entry=vocab_entry_data["entry"],
                pronunciation_ipa=vocab_entry_data["pronunciation_ipa"],
                pronunciation_spelling=vocab_entry_data["pronunciation_spelling"],
                description=vocab_entry_data["description"],
                date_created=vocab_entry_data["date_created"]
            ).exists()
        )
        self.client.post(
            reverse("api:vocab_entries_import"),
            json.dumps(data),
            content_type="application/json"
        )
        self.assertTrue(
            VocabEntry.objects.filter(
                language=vocab_entry_data["language"],
                entry=vocab_entry_data["entry"],
                pronunciation_ipa=vocab_entry_data["pronunciation_ipa"],
                pronunciation_spelling=vocab_entry_data["pronunciation_spelling"],
                description=vocab_entry_data["description"],
                date_created=vocab_entry_data["date_created"]
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
        found = resolve(reverse("api:vocab_entries_export"))
        self.assertEqual(
            found.func.__name__,
            VocabEntryExportView.as_view().__name__
        )

    def test_view_permission_classes(self):
        request = self.request_factory.get("/fake-path")
        request.user = self.user
        view = setup_test_view(VocabEntryExportView(), request)
        response = view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)
        permission_classes = (IsAuthenticated, IsSuperuser)
        self.assertEqual(permission_classes, view.permission_classes)

    def test_view_permissions(self):
        user_2 = User.objects.create(
            username="kfl7",
            email="kfl7@foo.com",
            first_name="Karen",
            last_name="Fuentes",
            password=self.pwd
        )

        # Not authenticated
        response = self.client.get(
            reverse("api:vocab_entries_export")
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated
        self.login_test_user(user_2.username)
        response = self.client.get(
            reverse("api:vocab_entries_export")
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated superuser
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse("api:vocab_entries_export")
        )
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_view_exports_vocab_entries_json(self):
        self.login_test_user(username=self.user.username)
        request = self.request_factory.get("/fake-path")
        request.user = self.user
        VocabEntry.objects.create(
            creator=self.user,
            entry="entry one",
            language="en"
        )
        VocabEntry.objects.create(
            creator=self.user,
            entry="entry two",
            language="es"
        )
        response = self.client.get(reverse(
            "api:vocab_entries_export"
        ))
        expected_data = export_vocab_entries(request=request)
        data = response.data
        self.assertEqual(len(data["vocab_entries"]), 2)
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
                "api:vocab_entries_language_export",
                kwargs={"language": "en"}
            )
        )
        self.assertEqual(
            found.func.__name__,
            VocabEntryLanguageExportView.as_view().__name__
        )

    def test_view_permissions(self):
        user_2 = User.objects.create(
            username="kfl7",
            email="kfl7@foo.com",
            first_name="Karen",
            last_name="Fuentes",
            password=self.pwd
        )

        # Non authenticated
        response = self.client.get(
            reverse(
                "api:vocab_entries_language_export",
                kwargs={"language": "en"}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated
        self.login_test_user(user_2.username)
        response = self.client.get(
            reverse(
                "api:vocab_entries_language_export",
                kwargs={"language": "en"}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated superuser
        self.login_test_user(self.user.username)
        response = self.client.get(
            reverse(
                "api:vocab_entries_language_export",
                kwargs={"language": "en"}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_view_exports_vocab_entries_json(self):
        self.login_test_user(username=self.user.username)
        request = self.request_factory.get("/fake-path")
        request.user = self.user
        VocabEntry.objects.create(
            creator=self.user,
            entry="entry one",
            language="en"
        )
        VocabEntry.objects.create(
            creator=self.user,
            entry="entry two",
            language="en"
        )
        VocabEntry.objects.create(
            creator=self.user,
            entry="entry three",
            language="es"
        )
        response = self.client.get(
            reverse(
                "api:vocab_entries_language_export",
                kwargs={"language": "es"}
            )
        )
        expected_data = export_vocab_entries(request=request, language="es")
        data = response.data
        self.assertEqual(len(data["vocab_entries"]), 1)
        self.assertEqual(expected_data, response.data)


class VocabSourceExportViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceExportViewTest, self).setUp()
        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="Test source",
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
                "api:vocab_source_export",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            )
        )
        self.assertEqual(
            found.func.__name__,
            VocabSourceExportView.as_view().__name__
        )

    def test_view_permission_classes(self):
        request = self.request_factory.get("/fake-path")
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
            username="kfl7",
            email="kfl7@foo.com",
            first_name="Karen",
            last_name="Fuentes",
            password=self.pwd
        )
        non_creator = User.objects.create(
            username="foo7",
            email="foo7@foo.com",
            first_name="Foo",
            last_name="Foo",
            password=self.pwd
        )
        vocab_source = VocabSource.objects.create(
            creator=creator,
            name="Another test source",
            source_type=VocabSource.BOOK
        )

        # Not authenticated
        response = self.client.get(
            reverse(
                "api:vocab_source_export",
                kwargs={"vocab_source_pk": vocab_source.id}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated non creator
        self.login_test_user(non_creator.username)
        response = self.client.get(
            reverse(
                "api:vocab_source_export",
                kwargs={"vocab_source_pk": vocab_source.id}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated creator
        self.login_test_user(creator.username)
        response = self.client.get(
            reverse(
                "api:vocab_source_export",
                kwargs={"vocab_source_pk": vocab_source.id}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

        # Authenticated non creator superuser
        self.login_test_user(self.user.username)
        self.assertTrue(self.user.is_superuser)
        response = self.client.get(
            reverse(
                "api:vocab_source_export",
                kwargs={"vocab_source_pk": vocab_source.id}
            )
        )
        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)


class VocabSourceImportViewTest(TestCommon):

    def setUp(self):
        super(VocabSourceImportViewTest, self).setUp()
        vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="Test source",
            source_type=VocabSource.BOOK
        )
        request = self.request_factory.get("/fake-path")
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
        found = resolve(reverse("api:vocab_source_import"))
        self.assertEqual(
            found.func.__name__,
            VocabSourceImportView.as_view().__name__
        )

    def test_view_imports_vocab_source_json(self):
        self.login_test_user(self.user.username)
        self.assertFalse(
            VocabSource.objects.filter(
                creator_id=self.vocab_source_data["creator_id"],
                name=self.vocab_source_data["vocab_source_data"]["name"]
            ).exists()
        )
        self.client.post(
            reverse("api:vocab_source_import"),
            json.dumps(self.vocab_source_data),
            content_type="application/json"
        )
        self.assertTrue(
            VocabSource.objects.filter(
                creator_id=self.vocab_source_data["creator_id"],
                name=self.vocab_source_data["vocab_source_data"]["name"]
            ).exists()
        )
