import json

from rest_framework import status as drf_status
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin,
    RetrieveModelMixin, UpdateModelMixin
)
from rest_framework.viewsets import GenericViewSet

from django.contrib.auth import get_user_model
from django.urls import reverse

from core.api.views_api import APIDefaultsMixin
from vocab.api.pagination import SmallPagination
from vocab.api.permissions import (
    ReadPermission, SourceCreatorPermission,
    SourceContextCreatorPermission, SourceContextEntryCreatorPermission
)
from vocab.api.views_vocab_context import (
    NestedVocabContextViewSet, NestedVocabContextEntryViewSet,
    VocabContextViewSet, VocabContextEntryViewSet,
)
from vocab.api.views_mixins import BatchMixin
from vocab.conf import settings
from vocab.models import (
    VocabContext, VocabContextAudio, VocabContextEntry,
    VocabEntry, VocabEntryTag, VocabSource
)
from vocab.serializers import (
    VocabContextSerializer, VocabContextEntrySerializer
)
from .base_test import TestCommon

User = get_user_model()

APP_NAME = "vocab"
URL_PREFIX = getattr(settings, "VOCAB_URL_PREFIX")


class VocabContextViewSetTest(TestCommon):

    def setUp(self):
        super(VocabContextViewSetTest, self).setUp()

        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="test source"
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="This is some content."
        )
        self.vocab_context_audio_1 = VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=self.vocab_context,
            name="Test audio 1",
            audio_url="https://www.foo.com/foo1.mp3"
        )
        self.vocab_context_audio_2 = VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=self.vocab_context,
            name="Test audio 22",
            audio_url="https://www.foo.com/foo22.mp3"
        )
        self.user_2 = User.objects.create_user(
            username="abc",
            first_name="Christopher",
            last_name="Sanders",
            email="abc@foo.com",
            password=self.pwd
        )

    def get_context_serializer_data(self, vocab_context):
        serializer = VocabContextSerializer(
            vocab_context,
            context={"request": self.get_dummy_request()}
        )
        return json.loads(serializer.json_data())

    def test_view_setup(self):
        view = VocabContextViewSet()
        self.assertEqual("pk", view.lookup_field)
        self.assertEqual("pk", view.lookup_url_kwarg)
        self.assertEqual(VocabContextSerializer, view.serializer_class)

        qs = VocabContext.objects.select_related("vocab_source")
        self.assertCountEqual(
            qs,
            view.queryset
        )
        self.assertEqual(str(qs.query), str(view.queryset.query))

        self.assertEqual(SmallPagination, view.pagination_class)

        permission_classes = [ReadPermission, SourceContextCreatorPermission]

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
            self.assertTrue(issubclass(VocabContextViewSet, class_name))

    def test_view_detail(self):
        response = self.client.get(
            reverse(
                "api:vocab-context-detail",
                kwargs={"pk": self.vocab_context.id}
            )
        )
        data = self.get_context_serializer_data(self.vocab_context)
        self.assertEqual(
            data,
            json.loads(response.content)
        )

    def test_view_detail_num_db_hits(self):
        with self.assertNumQueries(4):
            self.client.get(
                reverse(
                    "api:vocab-context-detail",
                    kwargs={"pk": self.vocab_context.id}
                ),
            )

    def test_view_list(self):
        vocab_source_2 = VocabSource.objects.create(
            creator=self.user,
            name="test source 2"
        )
        vocab_context_2 = VocabContext.objects.create(
            vocab_source=vocab_source_2,
            content="context 2"
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=vocab_context_2,
            name="Test audio 2",
            audio_url="https://www.foo.com/foo2.mp3"
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=vocab_context_2,
            name="Test audio 3",
            audio_url="https://www.foo.com/foo3.mp3"
        )
        data_1 = self.get_context_serializer_data(self.vocab_context)
        data_2 = self.get_context_serializer_data(vocab_context_2)

        expected_results = json.dumps({
            "next": None,
            "previous": None,
            "page_num": 1,
            "count": 2,
            "num_pages": 1,
            "results": [data_1, data_2]
        })

        response = self.client.get(
            reverse("api:vocab-context-list")
        )
        self.assertEqual(json.loads(expected_results), json.loads(response.content))

    def test_view_list_num_db_hits(self):
        with self.assertNumQueries(5):
            response = self.client.get(
                reverse("api:vocab-context-list")
            )
        vocab_source_2 = VocabSource.objects.create(
            creator=self.user,
            name="test source 2"
        )
        vocab_context_2 = VocabContext.objects.create(
            vocab_source=vocab_source_2,
            content="context 2"
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=vocab_context_2,
            name="Test audio 2",
            audio_url="https://www.foo.com/foo2.mp3"
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=vocab_context_2,
            name="Test audio 3",
            audio_url="https://www.foo.com/foo3.mp3"
        )
        with self.assertNumQueries(5):
            response = self.client.get(
                reverse("api:vocab-context-list")
            )
        vocab_context_3 = VocabContext.objects.create(
            vocab_source=vocab_source_2,
            content="context 3"
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=vocab_context_3,
            name="Test audio 4",
            audio_url="https://www.foo.com/foo4.mp3"
        )
        with self.assertNumQueries(5):
            response = self.client.get(
                reverse("api:vocab-context-list")
            )

    def test_view_update(self):
        self.login_test_user(self.user.username)

        vocab_context_data = {"content": "some content"}
        self.assertNotEqual(
            self.vocab_context.content,
            vocab_context_data["content"]
        )
        self.client.put(
            reverse(
                "api:vocab-context-detail",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=json.dumps(vocab_context_data),
            content_type="application/json"
        )
        self.vocab_context.refresh_from_db()
        self.assertEqual(
            self.vocab_context.content,
            vocab_context_data["content"]
        )

    def test_view_delete(self):
        self.login_test_user(self.user.username)

        id = self.vocab_context.id
        self.assertTrue(VocabContext.objects.filter(id=id).exists())
        self.client.delete(
            reverse("api:vocab-context-detail", kwargs={"pk": self.vocab_context.id})
        )
        self.assertFalse(VocabContext.objects.filter(id=id).exists())

    def test_add_vocab_entry(self):
        self.login_test_user(self.user.username)

        vocab_entry = VocabEntry.objects.create(
            language="es",
            entry="tergiversar"
        )
        vocab_entry_data = {"vocab_entry_id": vocab_entry.id}
        self.assertFalse(
            VocabContextEntry.objects.filter(
                vocab_context_id=self.vocab_context.id,
                vocab_entry_id=vocab_entry.id
            ).exists()
        )
        self.client.post(
            reverse(
                "api:vocab-context-add-vocab-entry",
                kwargs={"pk": self.vocab_context.id}
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
            language="es",
            entry="tergiversar"
        )
        tag = "tergiversa"
        data = {
            "vocab_entry_id": vocab_entry.id,
            "vocab_entry_tag": tag
        }
        VocabContextEntry.objects.create(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=vocab_entry.id
        )
        self.client.post(
            reverse(
                "api:vocab-context-add-vocab-entry-tag",
                kwargs={"pk": self.vocab_context.id}
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
            language="es",
            entry="tergiversar"
        )
        data = {
            "vocab_entry_id": vocab_entry.id,
        }
        VocabContextEntry.objects.create(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=vocab_entry.id
        )
        self.client.post(
            reverse(
                "api:vocab-context-remove-vocab-entry",
                kwargs={"pk": self.vocab_context.id}
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
            language="es",
            entry="tergiversar"
        )
        tag = "tergiversa"
        data = {
            "vocab_entry_id": vocab_entry.id,
            "vocab_entry_tag": tag
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
                "api:vocab-context-remove-vocab-entry-tag",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=data
        )

        tags = vocab_context_entry.get_vocab_entry_tags()
        self.assertNotIn(tag, tags)

    # Permissions
    def test_permissions_detail(self):
        # Not athenticated
        response = self.client.get(
            reverse(
                "api:vocab-context-detail",
                kwargs={"pk": self.vocab_context.id}
            ),
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_permissions_list(self):
        # Not authenticated
        response = self.client.get(
            reverse("api:vocab-context-list")
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_permissions_update(self):
        vocab_context_data = {"content": "some content"}

        # Not authenticated
        response = self.client.put(
            reverse(
                "api:vocab-context-detail",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=json.dumps(vocab_context_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated, not source owner
        self.client.logout()
        self.login_test_user(self.user_2.username)

        response = self.client.put(
            reverse(
                "api:vocab-context-detail",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=json.dumps(vocab_context_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Context source creator
        self.client.logout()
        self.login_test_user(self.user.username)

        response = self.client.put(
            reverse(
                "api:vocab-context-detail",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=json.dumps(vocab_context_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

        # Superuser not source creator
        self.client.logout()
        self.login_test_user(self.superuser.username)

        response = self.client.put(
            reverse(
                "api:vocab-context-detail",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=json.dumps(vocab_context_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_permissions_delete(self):
        # Not authenticated
        response = self.client.delete(
            reverse("api:vocab-context-detail", kwargs={"pk": self.vocab_context.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated not source owner
        self.client.logout()
        self.login_test_user(self.user_2.username)
        response = self.client.delete(
            reverse("api:vocab-context-detail", kwargs={"pk": self.vocab_context.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Source owner
        self.client.logout()
        self.login_test_user(self.user.username)
        response = self.client.delete(
            reverse("api:vocab-context-detail", kwargs={"pk": self.vocab_context.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_204_NO_CONTENT)

        # Superuser not source creator
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="This is some content."
        )

        self.client.logout()
        self.login_test_user(self.superuser.username)
        response = self.client.delete(
            reverse("api:vocab-context-detail", kwargs={"pk": self.vocab_context.id})
        )

        self.assertEqual(response.status_code, drf_status.HTTP_204_NO_CONTENT)

    def test_permissions_add_vocab_entry(self):
        vocab_entry = VocabEntry.objects.create(
            language="es",
            entry="tergiversar"
        )
        vocab_entry_data = {"vocab_entry_id": vocab_entry.id}

        # Not authenticated
        response = self.client.post(
            reverse(
                "api:vocab-context-add-vocab-entry",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=vocab_entry_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated not source creator
        self.client.logout()
        self.login_test_user(self.user_2.username)

        response = self.client.post(
            reverse(
                "api:vocab-context-add-vocab-entry",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=vocab_entry_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated source creator
        self.client.logout()
        self.login_test_user(self.user.username)

        response = self.client.post(
            reverse(
                "api:vocab-context-add-vocab-entry",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=vocab_entry_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_201_CREATED)

        # Superuser not source creator
        vocab_entry = VocabEntry.objects.create(
            language="es",
            entry="llover"
        )
        vocab_entry_data = {"vocab_entry_id": vocab_entry.id}

        self.client.logout()
        self.login_test_user(self.superuser.username)

        response = self.client.post(
            reverse(
                "api:vocab-context-add-vocab-entry",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=vocab_entry_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_201_CREATED)

    def test_permissions_add_vocab_entry_tag(self):
        vocab_entry = VocabEntry.objects.create(
            language="es",
            entry="tergiversar"
        )
        tag = "tergiversa"
        data = {
            "vocab_entry_id": vocab_entry.id,
            "vocab_entry_tag": tag
        }
        VocabContextEntry.objects.create(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=vocab_entry.id
        )

        # Not authenticated
        response = self.client.post(
            reverse(
                "api:vocab-context-add-vocab-entry-tag",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated not source creator
        self.client.logout()
        self.login_test_user(self.user_2.username)

        response = self.client.post(
            reverse(
                "api:vocab-context-add-vocab-entry-tag",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Source creator
        self.client.logout()
        self.login_test_user(self.user.username)

        response = self.client.post(
            reverse(
                "api:vocab-context-add-vocab-entry-tag",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_201_CREATED)

        # Superuser not source creator
        vocab_entry = VocabEntry.objects.create(
            language="es",
            entry="llover"
        )
        tag = "llueve"
        data = {
            "vocab_entry_id": vocab_entry.id,
            "vocab_entry_tag": tag
        }
        VocabContextEntry.objects.create(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=vocab_entry.id
        )

        self.client.logout()
        self.login_test_user(self.superuser.username)

        response = self.client.post(
            reverse(
                "api:vocab-context-add-vocab-entry-tag",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_201_CREATED)

    def test_permisssions_remove_vocab_entry(self):
        vocab_entry = VocabEntry.objects.create(
            language="es",
            entry="tergiversar"
        )
        data = {
            "vocab_entry_id": vocab_entry.id,
        }
        VocabContextEntry.objects.create(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=vocab_entry.id
        )

        # Not authenticated
        response = self.client.post(
            reverse(
                "api:vocab-context-remove-vocab-entry",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated not source creator
        self.client.logout()
        self.login_test_user(self.user_2.username)

        response = self.client.post(
            reverse(
                "api:vocab-context-remove-vocab-entry",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated not source creator
        self.client.logout()
        self.login_test_user(self.user.username)

        response = self.client.post(
            reverse(
                "api:vocab-context-remove-vocab-entry",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_204_NO_CONTENT)

        # Superuser not source creator
        vocab_entry = VocabEntry.objects.create(
            language="es",
            entry="llover"
        )
        data = {
            "vocab_entry_id": vocab_entry.id,
        }
        VocabContextEntry.objects.create(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=vocab_entry.id
        )

        self.client.logout()
        self.login_test_user(self.superuser.username)

        response = self.client.post(
            reverse(
                "api:vocab-context-remove-vocab-entry",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_204_NO_CONTENT)

    def test_permissions_remove_vocab_entry_tag(self):
        vocab_entry = VocabEntry.objects.create(
            language="es",
            entry="tergiversar"
        )
        tag = "tergiversa"
        data = {
            "vocab_entry_id": vocab_entry.id,
            "vocab_entry_tag": tag
        }
        vocab_context_entry = VocabContextEntry.objects.create(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=vocab_entry.id
        )
        vocab_context_entry.add_vocab_entry_tag(tag)

        # Not authenticated
        response = self.client.post(
            reverse(
                "api:vocab-context-remove-vocab-entry-tag",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated not source creator
        self.client.logout()
        self.login_test_user(self.user_2.username)

        response = self.client.post(
            reverse(
                "api:vocab-context-remove-vocab-entry-tag",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Source creator
        self.client.logout()
        self.login_test_user(self.user.username)

        response = self.client.post(
            reverse(
                "api:vocab-context-remove-vocab-entry-tag",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_204_NO_CONTENT)

        # Superuser not source creator
        vocab_entry = VocabEntry.objects.create(
            language="es",
            entry="llover"
        )
        tag = "llueve"
        data = {
            "vocab_entry_id": vocab_entry.id,
            "vocab_entry_tag": tag
        }
        vocab_context_entry = VocabContextEntry.objects.create(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=vocab_entry.id
        )
        vocab_context_entry.add_vocab_entry_tag(tag)

        self.client.logout()
        self.login_test_user(self.superuser.username)

        response = self.client.post(
            reverse(
                "api:vocab-context-remove-vocab-entry-tag",
                kwargs={"pk": self.vocab_context.id}
            ),
            data=data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_204_NO_CONTENT)


class NestedVocabContextViewSetTest(TestCommon):

    def setUp(self):
        super(NestedVocabContextViewSetTest, self).setUp()

        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="test source 1"
        )
        self.vocab_context_1 = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="test content 1"
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=self.vocab_context_1,
            name="Test audio 1",
            audio_url="https://www.foo.com/foo1.mp3"
        )
        self.vocab_context_2 = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="test content 2"
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=self.vocab_context_2,
            name="Test audio 2",
            audio_url="https://www.foo.com/foo2.mp3"
        )
        self.vocab_source_2 = VocabSource.objects.create(
            creator=self.user,
            name="test source 2"
        )
        self.vocab_context_3 = VocabContext.objects.create(
            vocab_source=self.vocab_source_2,
            content="test content 3"
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=self.vocab_context_3,
            name="Test audio 3",
            audio_url="https://www.foo.com/foo3.mp3"
        )
        self.vocab_context_4 = VocabContext.objects.create(
            vocab_source=self.vocab_source_2,
            content="test content 4"
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=self.vocab_context_4,
            name="Test audio 4",
            audio_url="https://www.foo.com/foo4.mp3"
        )
        self.user_2 = User.objects.create_user(
            username="abc",
            first_name="Christopher",
            last_name="Sanders",
            email="abc@foo.com",
            password=self.pwd
        )

    def get_context_serializer_data(self, vocab_context):
        serializer = VocabContextSerializer(
            vocab_context,
            context={"request": self.get_dummy_request()}
        )
        return json.loads(serializer.json_data())

    def test_view_setup(self):
        view = NestedVocabContextViewSet()
        self.assertEqual("pk", view.lookup_field)
        self.assertEqual("pk", view.lookup_url_kwarg)
        self.assertEqual(VocabContextSerializer, view.serializer_class)
        self.assertEqual(SmallPagination, view.pagination_class)

        qs = VocabContext.objects.select_related("vocab_source")
        self.assertCountEqual(
            qs,
            view.queryset
        )
        self.assertEqual(str(qs.query), str(view.queryset.query))

        permission_classes = [ReadPermission, SourceCreatorPermission]

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
                issubclass(NestedVocabContextViewSet, class_name)
            )

    def test_view_create(self):
        self.login_test_user(self.user.username)

        vocab_context_data = {
            "content": "test content"
        }
        self.assertFalse(
            VocabContext.objects.filter(
                vocab_source=self.vocab_source,
                content=vocab_context_data["content"]
            ).exists()
        )
        self.client.post(
            reverse(
                "api:nested-vocab-context-list",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            ),
            data=vocab_context_data
        )
        self.assertTrue(
            VocabContext.objects.filter(
                vocab_source=self.vocab_source,
                content=vocab_context_data["content"]
            ).exists()
        )

    def test_view_list(self):
        self.login_test_user(self.user.username)

        # Source 1
        data_1 = self.get_context_serializer_data(self.vocab_context_1)
        data_2 = self.get_context_serializer_data(self.vocab_context_2)
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
                "api:nested-vocab-context-list",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            )
        )

        self.assertEqual(json.loads(expected_results), json.loads(response.content))

        # Source 2
        data_3 = self.get_context_serializer_data(self.vocab_context_3)
        data_4 = self.get_context_serializer_data(self.vocab_context_4)
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
                "api:nested-vocab-context-list",
                kwargs={"vocab_source_pk": self.vocab_source_2.id}
            )
        )
        self.assertEqual(json.loads(expected_results), json.loads(response.content))

    def test_view_list_num_db_hits(self):
        self.login_test_user(self.user.username)

        with self.assertNumQueries(8):
            response = self.client.get(
                reverse(
                    "api:nested-vocab-context-list",
                    kwargs={"vocab_source_pk": self.vocab_source.id}
                )
            )

        vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="test content"
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=vocab_context,
            name="Test audio xyz",
            audio_url="https://www.foo.com/fooxyz.mp3"
        )

        with self.assertNumQueries(8):
            response = self.client.get(
                reverse(
                    "api:nested-vocab-context-list",
                    kwargs={"vocab_source_pk": self.vocab_source.id}
                )
            )

    def test_view_list_contexts_with_audios(self):
        vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="test source"
        )
        vocab_context_1_audio = VocabContext.objects.create(
            vocab_source=vocab_source,
            content="test content 1"
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=vocab_context_1_audio,
            name="Test audio",
            audio_url="https://www.foo.com/foo1.mp3"
        )
        vocab_context_0_audio = VocabContext.objects.create(
            vocab_source=vocab_source,
            content="test content 2"
        )

        data_1 = self.get_context_serializer_data(vocab_context_1_audio)
        data_2 = self.get_context_serializer_data(vocab_context_0_audio)
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
                "api:nested-vocab-context-list",
                kwargs={"vocab_source_pk": vocab_source.id}
            )
        )
        self.assertEqual(
            json.loads(expected_results), json.loads(response.content)
        )

        expected_results = json.dumps({
            "next": None,
            "previous": None,
            "page_num": 1,
            "count": 1,
            "num_pages": 1,
            "results": [data_1]
        })
        response = self.client.get(
            reverse(
                "api:nested-vocab-context-list",
                kwargs={"vocab_source_pk": vocab_source.id}
            ),
            {"filter_audios": True},
        )
        self.assertEqual(
            json.loads(expected_results), json.loads(response.content)
        )

    # Permissions

    def test_permissions_create(self):
        vocab_context_data = {
            "content": "test content"
        }

        # Not authenticated
        response = self.client.post(
            reverse(
                "api:nested-vocab-context-list",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            ),
            data=vocab_context_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated not source creator
        self.client.logout()
        self.login_test_user(self.user_2.username)

        response = self.client.post(
            reverse(
                "api:nested-vocab-context-list",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            ),
            data=vocab_context_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Source creator
        self.client.logout()
        self.login_test_user(self.user.username)

        response = self.client.post(
            reverse(
                "api:nested-vocab-context-list",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            ),
            data=vocab_context_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_201_CREATED)

        # Superuser not source creator
        vocab_context_data = {
            "content": "more test content"
        }

        self.client.logout()
        self.login_test_user(self.superuser.username)

        response = self.client.post(
            reverse(
                "api:nested-vocab-context-list",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            ),
            data=vocab_context_data
        )

        self.assertEqual(response.status_code, drf_status.HTTP_201_CREATED)

    def test_permissions_list(self):
        # Not authenticated
        response = self.client.get(
            reverse(
                "api:nested-vocab-context-list",
                kwargs={"vocab_source_pk": self.vocab_source.id}
            )
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)


class VocabContextEntryViewSetTest(TestCommon):

    def setUp(self):
        super(VocabContextEntryViewSetTest, self).setUp()

        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="test source"
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="This is some content."
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=self.vocab_context,
            name="Test audio 1",
            audio_url="https://www.foo.com/foo1.mp3"
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=self.vocab_context,
            name="Test audio 2",
            audio_url="https://www.foo.com/foo2.mp3"
        )
        self.vocab_entry = VocabEntry.objects.create(
            language="es",
            entry="tergiversar"
        )
        self.vocab_context_entry = VocabContextEntry.objects.create(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=self.vocab_entry.id
        )
        VocabEntryTag.objects.create(
            vocab_context_entry=self.vocab_context_entry,
            content="tergiversa"
        )
        self.user_2 = User.objects.create_user(
            username="abc",
            first_name="Christopher",
            last_name="Sanders",
            email="abc@foo.com",
            password=self.pwd
        )

    def get_context_entry_serializer_data(self, vocab_context_entry):
        serializer = VocabContextEntrySerializer(
            vocab_context_entry,
            context={"request": self.get_dummy_request()}
        )
        return json.loads(serializer.json_data())

    def test_view_setup(self):
        view = VocabContextEntryViewSet()
        self.assertEqual("pk", view.lookup_field)
        self.assertEqual("pk", view.lookup_url_kwarg)
        self.assertEqual(VocabContextEntrySerializer, view.serializer_class)
        self.assertEqual(SmallPagination, view.pagination_class)

        qs = VocabContextEntry.objects.select_related(
            "vocab_entry",
            "vocab_context",
            "vocab_context__vocab_source"
        )
        qs = qs.prefetch_related("vocab_entry_tags")

        self.assertCountEqual(qs, view.queryset)
        self.assertEqual(str(qs.query), str(view.queryset.query))

        permission_classes = [ReadPermission, SourceContextEntryCreatorPermission]

        self.assertEqual(permission_classes, view.permission_classes)

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

        response = self.client.get(
            reverse(
                "api:vocab-context-entry-detail",
                kwargs={"pk": self.vocab_context_entry.id}
            ),
        )
        data = self.get_context_entry_serializer_data(self.vocab_context_entry)

        self.assertEqual(
            data,
            json.loads(response.content)
        )

    def test_view_list_num_db_hits(self):
        with self.assertNumQueries(5):
            response = self.client.get(
                reverse(
                    "api:vocab-context-entry-list",
                )
            )
        vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="This is some content."
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=vocab_context,
            name="Test audio 3",
            audio_url="https://www.foo.com/foo3.mp3"
        )
        VocabContextAudio.objects.create(
            creator=self.user,
            vocab_context=vocab_context,
            name="Test audio 4",
            audio_url="https://www.foo.com/foo4.mp3"
        )
        vocab_entry = VocabEntry.objects.create(
            language="es",
            entry="verificar"
        )
        vocab_context_entry = VocabContextEntry.objects.create(
            vocab_context_id=vocab_context.id,
            vocab_entry_id=vocab_entry.id
        )
        VocabEntryTag.objects.create(
            vocab_context_entry=vocab_context_entry,
            content="verifica"
        )
        with self.assertNumQueries(5):
            response = self.client.get(
                reverse(
                    "api:vocab-context-entry-list",
                )
            )

    def test_view_delete(self):
        self.login_test_user(self.user.username)

        data = {
            "vocab_entry_id": self.vocab_context_entry.vocab_entry_id,
            "vocab_context_id": self.vocab_context_entry.vocab_context_id
        }

        self.assertTrue(
            VocabContextEntry.objects.filter(
                vocab_entry_id=data["vocab_entry_id"],
                vocab_context_id=data["vocab_context_id"]
            ).exists()
        )
        self.client.delete(
            reverse(
                "api:vocab-context-entry-detail",
                kwargs={"pk": self.vocab_context_entry.id}
            )
        )
        self.assertFalse(
            VocabContextEntry.objects.filter(
                vocab_entry_id=data["vocab_entry_id"],
                vocab_context_id=data["vocab_context_id"]
            ).exists()
        )

    # Permissions

    def test_permissions_detail(self):
        # Not authenticated
        response = self.client.get(
            reverse(
                "api:vocab-context-entry-detail",
                kwargs={"pk": self.vocab_context_entry.id}
            ),
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_permissions_list(self):
        # Not authenticated
        response = self.client.get(
            reverse(
                "api:vocab-context-entry-list",
            )
        )

        self.assertEqual(response.status_code, drf_status.HTTP_200_OK)

    def test_permissions_delete(self):

        # Not authenticated
        response = self.client.delete(
            reverse(
                "api:vocab-context-entry-detail",
                kwargs={"pk": self.vocab_context_entry.id}
            )
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Authenticated not source creator
        self.client.logout()
        self.login_test_user(self.user_2.username)

        response = self.client.delete(
            reverse(
                "api:vocab-context-entry-detail",
                kwargs={"pk": self.vocab_context_entry.id}
            )
        )

        self.assertEqual(response.status_code, drf_status.HTTP_403_FORBIDDEN)

        # Source creator
        self.client.logout()
        self.login_test_user(self.user.username)

        response = self.client.delete(
            reverse(
                "api:vocab-context-entry-detail",
                kwargs={"pk": self.vocab_context_entry.id}
            )
        )

        self.assertEqual(response.status_code, drf_status.HTTP_204_NO_CONTENT)

        # Superuser not source creator
        self.vocab_context_entry = VocabContextEntry.objects.create(
            vocab_context_id=self.vocab_context.id,
            vocab_entry_id=self.vocab_entry.id
        )

        self.client.logout()
        self.login_test_user(self.superuser.username)

        response = self.client.delete(
            reverse(
                "api:vocab-context-entry-detail",
                kwargs={"pk": self.vocab_context_entry.id}
            )
        )

        self.assertEqual(response.status_code, drf_status.HTTP_204_NO_CONTENT)


class NestedVocabContextEntryViewSetTest(TestCommon):

    def setUp(self):
        super(NestedVocabContextEntryViewSetTest, self).setUp()

        self.vocab_source = VocabSource.objects.create(
            creator=self.user,
            name="test source"
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content="This is some content."
        )
        self.user_2 = User.objects.create_user(
            username="abc",
            first_name="Christopher",
            last_name="Sanders",
            email="abc@foo.com",
            password=self.pwd
        )

    def get_context_entry_serializer_data(self, vocab_context_entry):
        serializer = VocabContextEntrySerializer(
            vocab_context_entry,
            context={"request": self.get_dummy_request()}
        )
        return json.loads(serializer.json_data())

    def test_view_setup(self):
        view = NestedVocabContextEntryViewSet()
        self.assertEqual("pk", view.lookup_field)
        self.assertEqual("pk", view.lookup_url_kwarg)
        self.assertEqual(VocabContextEntrySerializer, view.serializer_class)
        self.assertEqual(SmallPagination, view.pagination_class)

        qs = VocabContextEntry.objects.select_related(
            "vocab_entry",
            "vocab_context",
            "vocab_context__vocab_source"
        )
        qs = qs.prefetch_related("vocab_entry_tags")

        self.assertCountEqual(qs, view.queryset)
        self.assertEqual(str(qs.query), str(view.queryset.query))

        permission_classes = [ReadPermission, SourceContextCreatorPermission]

        self.assertEqual(permission_classes, view.permission_classes)

    # def test_view_create(self):
    #     self.login_test_user(self.user.username)

    #     vocab_context_data = {
    #         "content": "test content"
    #     }
    #     self.assertFalse(
    #         VocabContext.objects.filter(
    #             vocab_source=self.vocab_source,
    #             content=vocab_context_data["content"]
    #         ).exists()
    #     )
    #     self.client.post(
    #         reverse(
    #             "api:nested-vocab-context-list",
    #             kwargs={"vocab_source_pk": self.vocab_source.id}
    #         ),
    #         data=vocab_context_data
    #     )
    #     self.assertTrue(
    #         VocabContext.objects.filter(
    #             vocab_source=self.vocab_source,
    #             content=vocab_context_data["content"]
    #         ).exists()
    #     )
