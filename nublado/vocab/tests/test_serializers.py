import json

from rest_framework.reverse import reverse as drf_reverse

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from ..models import (
    VocabDefinition, VocabEntry, VocabEntryTag, VocabContext, VocabContextEntry,
    VocabProject, VocabSource
)
from ..serializers import (
    VocabDefinitionSerializer, VocabEntrySerializer, VocabContextSerializer,
    VocabContextEntrySerializer, VocabProjectSerializer, VocabSourceSerializer
)

User = get_user_model()


class TestCommon(TestCase):

    def setUp(self):
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_user(
            username='cfs',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@cfs.com',
            password=self.pwd
        )


class VocabProjectSerializerTest(TestCommon):

    def setUp(self):
        super(VocabProjectSerializerTest, self).setUp()
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.request = self.client.get(reverse('api:vocab-project-list')).wsgi_request
        self.serializer = VocabProjectSerializer(
            self.vocab_project,
            context={'request': self.request}
        )

    def test_minimal_data_fields(self):
        expected_minimal_data = ['name', 'description', 'date_created']
        self.assertCountEqual(expected_minimal_data, self.serializer.minimal_data_fields)

    def test_get_minimal_data(self):
        expected_data = {
            'name': self.vocab_project.name,
            'description': self.vocab_project.description,
            'date_created': self.vocab_project.date_created.isoformat()
        }
        self.assertEqual(expected_data, self.serializer.get_minimal_data())

    def test_serialized_data(self):
        expected_data = {
            'url': drf_reverse(
                'api:vocab-project-detail',
                kwargs={'pk': self.vocab_project.id},
                request=self.request
            ),
            'id': self.vocab_project.id,
            'owner_id': self.user.id,
            'owner_url': drf_reverse(
                'api:user-detail',
                kwargs={'username': self.user.username},
                request=self.request
            ),
            'vocab_sources_url': drf_reverse(
                'api:nested-vocab-source-list',
                kwargs={'vocab_project_pk': self.vocab_project.id},
                request=self.request
            ),
            'name': self.vocab_project.name,
            'description': self.vocab_project.description,
            'slug': self.vocab_project.slug,
            'date_created': self.vocab_project.date_created.isoformat(),
            'date_updated': self.vocab_project.date_updated.isoformat(),
        }
        data = self.serializer.data
        self.assertEqual(expected_data, data)

    def test_json_data(self):
        expected_json_data = json.dumps({
            'url': drf_reverse(
                'api:vocab-project-detail',
                kwargs={'pk': self.vocab_project.id},
                request=self.request
            ),
            'id': self.vocab_project.id,
            'owner_id': str(self.user.id),
            'owner_url': drf_reverse(
                'api:user-detail',
                kwargs={'username': self.user.username},
                request=self.request
            ),
            'vocab_sources_url': drf_reverse(
                'api:nested-vocab-source-list',
                kwargs={'vocab_project_pk': self.vocab_project.id},
                request=self.request
            ),
            'name': self.vocab_project.name,
            'description': self.vocab_project.description,
            'slug': self.vocab_project.slug,
            'date_created': self.vocab_project.date_created.isoformat(),
            'date_updated': self.vocab_project.date_updated.isoformat(),
        })
        json_data = self.serializer.json_data()
        self.assertEqual(json.loads(expected_json_data), json.loads(json_data))

    def test_validation_no_name(self):
        data = {'name': ''}
        self.serializer = VocabProjectSerializer(self.vocab_project, data=data, partial=True)
        self.assertFalse(self.serializer.is_valid())
        self.assertEqual(len(self.serializer.errors), 1)
        self.assertTrue(self.serializer.errors['name'])


class VocabEntrySerializerTest(TestCommon):

    def setUp(self):
        super(VocabEntrySerializerTest, self).setUp()
        self.vocab_entry = VocabEntry.objects.create(
            language='en',
            entry='hello'
        )
        self.request = self.client.get(reverse('api:vocab-source-list')).wsgi_request
        self.serializer = VocabEntrySerializer(
            self.vocab_entry,
            context={'request': self.request}
        )

    def test_minimal_data_fields(self):
        expected_minimal_data = [
            'entry', 'language', 'description',
            'pronunciation_ipa', 'pronunciation_spelling', 'date_created'
        ]
        self.assertCountEqual(expected_minimal_data, self.serializer.minimal_data_fields)

    def test_get_minimal_data(self):
        expected_data = {
            'entry': self.vocab_entry.entry,
            'language': self.vocab_entry.language,
            'description': self.vocab_entry.description,
            'pronunciation_ipa': self.vocab_entry.pronunciation_ipa,
            'pronunciation_spelling': self.vocab_entry.pronunciation_spelling,
            'date_created': self.vocab_entry.date_created.isoformat()
        }
        self.assertEqual(expected_data, self.serializer.get_minimal_data())

    def test_serialized_data(self):
        expected_data = {
            'url': drf_reverse(
                'api:vocab-entry-detail',
                kwargs={'pk': self.vocab_entry.id},
                request=self.request
            ),
            'id': self.vocab_entry.id,
            'language': self.vocab_entry.language,
            'entry': self.vocab_entry.entry,
            'description': self.vocab_entry.description,
            'pronunciation_ipa': self.vocab_entry.pronunciation_ipa,
            'pronunciation_spelling': self.vocab_entry.pronunciation_spelling,
            'slug': self.vocab_entry.slug,
            'vocab_definitions_url': drf_reverse(
                'api:nested-vocab-definition-list',
                kwargs={'vocab_entry_pk': self.vocab_entry.id},
                request=self.request
            ),
            'date_created': self.vocab_entry.date_created.isoformat(),
            'date_updated': self.vocab_entry.date_updated.isoformat(),
        }
        data = self.serializer.data
        self.assertEqual(expected_data, data)

    def test_json_data(self):
        expected_json_data = json.dumps({
            'url': drf_reverse(
                'api:vocab-entry-detail',
                kwargs={'pk': self.vocab_entry.id},
                request=self.request
            ),
            'id': self.vocab_entry.id,
            'language': self.vocab_entry.language,
            'entry': self.vocab_entry.entry,
            'description': self.vocab_entry.description,
            'pronunciation_ipa': self.vocab_entry.pronunciation_ipa,
            'pronunciation_spelling': self.vocab_entry.pronunciation_spelling,
            'slug': self.vocab_entry.slug,
            'vocab_definitions_url': drf_reverse(
                'api:nested-vocab-definition-list',
                kwargs={'vocab_entry_pk': self.vocab_entry.id},
                request=self.request
            ),
            'date_created': self.vocab_entry.date_created.isoformat(),
            'date_updated': self.vocab_entry.date_updated.isoformat(),
        })
        json_data = self.serializer.json_data()
        self.assertEqual(json.loads(expected_json_data), json.loads(json_data))

    def test_validation_no_entry(self):
        data = {'entry': ''}
        self.serializer = VocabEntrySerializer(
            self.vocab_entry,
            data=data,
            partial=True
        )
        self.assertFalse(self.serializer.is_valid())
        self.assertEqual(len(self.serializer.errors), 1)
        self.assertTrue(self.serializer.errors['entry'])


class VocabDefinitionSerializerTest(TestCommon):

    def setUp(self):
        super(VocabDefinitionSerializerTest, self).setUp()
        self.vocab_entry = VocabEntry.objects.create(
            language='en',
            entry='hello'
        )
        self.vocab_definition = VocabDefinition.objects.create(
            vocab_entry=self.vocab_entry,
            lexical_category=VocabDefinition.NOUN,
            definition='hello'
        )
        self.request = self.client.get(reverse('api:vocab-definition-list')).wsgi_request
        self.serializer = VocabDefinitionSerializer(
            self.vocab_definition,
            context={'request': self.request}
        )

    def test_minimal_data_fields(self):
        expected_minimal_data = [
            'lexical_category', 'definition',
            'date_created'
        ]
        self.assertCountEqual(expected_minimal_data, self.serializer.minimal_data_fields)

    def test_get_minimal_data(self):
        expected_data = {
            'lexical_category': self.vocab_definition.lexical_category,
            'definition': self.vocab_definition.definition,
            'date_created': self.vocab_definition.date_created.isoformat()
        }
        self.assertEqual(expected_data, self.serializer.get_minimal_data())

    def test_serialized_data(self):
        expected_data = {
            'url': drf_reverse(
                'api:vocab-definition-detail',
                kwargs={'pk': self.vocab_definition.id},
                request=self.request
            ),
            'id': self.vocab_definition.id,
            'vocab_entry_id': self.vocab_entry.id,
            'vocab_entry_url': drf_reverse(
                'api:vocab-entry-detail',
                kwargs={'pk': self.vocab_entry.id},
                request=self.request
            ),
            'lexical_category': self.vocab_definition.lexical_category,
            'lexical_category_name': self.vocab_definition.get_lexical_category_display(),
            'definition': self.vocab_definition.definition,
            'date_created': self.vocab_definition.date_created.isoformat(),
            'date_updated': self.vocab_definition.date_updated.isoformat(),
        }
        data = self.serializer.data
        self.assertEqual(expected_data, data)

    def test_json_data(self):
        expected_json_data = json.dumps({
            'url': drf_reverse(
                'api:vocab-definition-detail',
                kwargs={'pk': self.vocab_definition.id},
                request=self.request
            ),
            'id': self.vocab_definition.id,
            'vocab_entry_id': self.vocab_entry.id,
            'vocab_entry_url': drf_reverse(
                'api:vocab-entry-detail',
                kwargs={'pk': self.vocab_entry.id},
                request=self.request
            ),
            'lexical_category': self.vocab_definition.lexical_category,
            'lexical_category_name': self.vocab_definition.get_lexical_category_display(),
            'definition': self.vocab_definition.definition,
            'date_created': self.vocab_definition.date_created.isoformat(),
            'date_updated': self.vocab_definition.date_updated.isoformat(),
        })
        json_data = self.serializer.json_data()
        self.assertEqual(json.loads(expected_json_data), json.loads(json_data))


class VocabSourceSerializerTest(TestCommon):

    def setUp(self):
        super(VocabSourceSerializerTest, self).setUp()
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='Test Source',
            description='A test source'
        )
        self.request = self.client.get(reverse('api:vocab-source-list')).wsgi_request
        self.serializer = VocabSourceSerializer(
            self.vocab_source,
            context={'request': self.request}
        )

    def test_minimal_data_fields(self):
        expected_minimal_data = ['name', 'source_type', 'description', 'date_created']
        self.assertCountEqual(expected_minimal_data, self.serializer.minimal_data_fields)

    def test_get_minimal_data(self):
        expected_data = {
            'name': self.vocab_source.name,
            'description': self.vocab_source.description,
            'source_type': self.vocab_source.source_type,
            'date_created': self.vocab_source.date_created.isoformat()
        }
        self.assertEqual(expected_data, self.serializer.get_minimal_data())

    def test_serialized_data(self):
        expected_data = {
            'url': drf_reverse(
                'api:vocab-source-detail',
                kwargs={'pk': self.vocab_source.id},
                request=self.request
            ),
            'id': self.vocab_source.id,
            'project_id': self.vocab_project.id,
            'project_url': drf_reverse(
                'api:vocab-project-detail',
                kwargs={'pk': self.vocab_project.id},
                request=self.request
            ),
            'creator_id': self.user.id,
            'creator_url': drf_reverse(
                'api:user-detail',
                kwargs={'username': self.user.username},
                request=self.request
            ),
            'name': self.vocab_source.name,
            'description': self.vocab_source.description,
            'slug': self.vocab_source.slug,
            'source_type': self.vocab_source.source_type,
            'source_type_name': self.vocab_source.get_source_type_display(),
            'vocab_contexts_url': drf_reverse(
                'api:nested-vocab-context-list',
                kwargs={'vocab_source_pk': self.vocab_source.id},
                request=self.request
            ),
            'date_created': self.vocab_source.date_created.isoformat(),
            'date_updated': self.vocab_source.date_updated.isoformat(),
        }
        data = self.serializer.data
        self.assertEqual(expected_data, data)

    def test_json_data(self):
        expected_json_data = json.dumps({
            'url': drf_reverse(
                'api:vocab-source-detail',
                kwargs={'pk': self.vocab_source.pk},
                request=self.request
            ),
            'project_id': self.vocab_project.id,
            'project_url': drf_reverse(
                'api:vocab-project-detail',
                kwargs={'pk': self.vocab_project.id},
                request=self.request
            ),
            'id': self.vocab_source.id,
            'creator_id': str(self.user.id),
            'creator_url': drf_reverse(
                'api:user-detail',
                kwargs={'username': self.user.username},
                request=self.request
            ),
            'name': self.vocab_source.name,
            'description': self.vocab_source.description,
            'slug': self.vocab_source.slug,
            'source_type': self.vocab_source.source_type,
            'source_type_name': self.vocab_source.get_source_type_display(),
            'vocab_contexts_url': drf_reverse(
                'api:nested-vocab-context-list',
                kwargs={'vocab_source_pk': self.vocab_source.id},
                request=self.request
            ),
            'date_created': self.vocab_source.date_created.isoformat(),
            'date_updated': self.vocab_source.date_updated.isoformat(),
        })
        json_data = self.serializer.json_data()
        self.assertEqual(json.loads(expected_json_data), json.loads(json_data))

    def test_validation_no_name(self):
        data = {'name': ''}
        self.serializer = VocabSourceSerializer(self.vocab_source, data=data, partial=True)
        self.assertFalse(self.serializer.is_valid())
        self.assertEqual(len(self.serializer.errors), 1)
        self.assertTrue(self.serializer.errors['name'])


class VocabContextSerializerTest(TestCommon):

    def setUp(self):
        super(VocabContextSerializerTest, self).setUp()
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='Test Source',
            description='A test source'
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='Hello'
        )
        self.request = self.client.get(reverse('api:vocab-source-list')).wsgi_request
        self.serializer = VocabContextSerializer(
            self.vocab_context,
            context={'request': self.request}
        )

    def test_minimal_data_fields(self):
        expected_minimal_data = ['content', 'date_created']
        self.assertCountEqual(expected_minimal_data, self.serializer.minimal_data_fields)

    def test_get_minimal_data(self):
        expected_data = {
            'content': self.vocab_context.content,
            'date_created': self.vocab_context.date_created.isoformat()
        }
        self.assertEqual(expected_data, self.serializer.get_minimal_data())

    def test_serialized_data(self):
        expected_data = {
            'url': drf_reverse(
                'api:vocab-context-detail',
                kwargs={'pk': self.vocab_context.id},
                request=self.request
            ),
            'id': self.vocab_context.id,
            'vocab_source_id': self.vocab_source.id,
            'vocab_source_url': drf_reverse(
                'api:vocab-source-detail',
                kwargs={'pk': self.vocab_source.id},
                request=self.request
            ),
            'content': self.vocab_context.content,
            'vocab_entries_url': drf_reverse(
                'api:nested-vocab-context-entry-list',
                kwargs={'vocab_context_pk': self.vocab_context.id},
                request=self.request
            ),
            'date_created': self.vocab_context.date_created.isoformat(),
            'date_updated': self.vocab_context.date_updated.isoformat(),
        }
        data = self.serializer.data
        self.assertEqual(expected_data, data)

    def test_json_data(self):
        expected_json_data = json.dumps({
            'url': drf_reverse(
                'api:vocab-context-detail',
                kwargs={'pk': self.vocab_context.id},
                request=self.request
            ),
            'id': self.vocab_context.id,
            'vocab_source_id': self.vocab_source.id,
            'vocab_source_url': drf_reverse(
                'api:vocab-source-detail',
                kwargs={'pk': self.vocab_source.id},
                request=self.request
            ),
            'content': self.vocab_context.content,
            'vocab_entries_url': drf_reverse(
                'api:nested-vocab-context-entry-list',
                kwargs={'vocab_context_pk': self.vocab_context.id},
                request=self.request
            ),
            'date_created': self.vocab_context.date_created.isoformat(),
            'date_updated': self.vocab_context.date_updated.isoformat(),
        })
        json_data = self.serializer.json_data()
        self.assertEqual(json.loads(expected_json_data), json.loads(json_data))

    def test_validation_no_content(self):
        data = {'content': ''}
        self.serializer = VocabContextSerializer(
            self.vocab_context,
            data=data,
            partial=True
        )
        self.assertFalse(self.serializer.is_valid())
        self.assertEqual(len(self.serializer.errors), 1)
        self.assertTrue(self.serializer.errors['content'])


class VocabContextEntrySerializerTest(TestCommon):

    def setUp(self):
        super(VocabContextEntrySerializerTest, self).setUp()
        self.vocab_project = VocabProject.objects.create(
            owner=self.user,
            name='test project'
        )
        self.vocab_source = VocabSource.objects.create(
            vocab_project=self.vocab_project,
            creator=self.user,
            name='Test Source',
            description='A test source'
        )
        self.vocab_context = VocabContext.objects.create(
            vocab_source=self.vocab_source,
            content='Hello'
        )
        self.vocab_entry = VocabEntry.objects.create(
            language='es',
            entry='tergiversar'
        )
        self.vocab_context_entry = VocabContextEntry.objects.create(
            vocab_context=self.vocab_context,
            vocab_entry=self.vocab_entry
        )
        self.vocab_tag = VocabEntryTag.objects.create(
            vocab_context_entry=self.vocab_context_entry,
            content='tergiversa'
        )
        self.request = self.client.get(reverse('api:vocab-source-list')).wsgi_request
        self.serializer = VocabContextEntrySerializer(
            self.vocab_context_entry,
            context={'request': self.request}
        )

    def test_minimal_data_fields(self):
        expected_minimal_data = ['vocab_entry', 'vocab_context', 'vocab_entry_tags', 'date_created']
        self.assertCountEqual(expected_minimal_data, self.serializer.minimal_data_fields)

    def test_serialized_data(self):
        expected_data = {
            'url': drf_reverse(
                'api:vocab-context-entry-detail',
                kwargs={'pk': self.vocab_context_entry.id},
                request=self.request
            ),
            'id': self.vocab_context_entry.id,
            'vocab_entry_id': self.vocab_entry.id,
            'vocab_entry_url': drf_reverse(
                'api:vocab-entry-detail',
                kwargs={'pk': self.vocab_entry.id},
                request=self.request
            ),
            'vocab_entry': self.vocab_entry.entry,
            'vocab_context_url': drf_reverse(
                'api:vocab-context-detail',
                kwargs={'pk': self.vocab_context.id},
                request=self.request
            ),
            'vocab_context': self.vocab_context.content,
            'vocab_entry_tags': [self.vocab_tag.content],
            'date_created': self.vocab_context_entry.date_created.isoformat(),
            'date_updated': self.vocab_context_entry.date_updated.isoformat(),
        }
        data = self.serializer.data
        self.assertEqual(expected_data, data)

    def test_json_data(self):
        expected_json_data = json.dumps({
            'url': drf_reverse(
                'api:vocab-context-entry-detail',
                kwargs={'pk': self.vocab_context_entry.id},
                request=self.request
            ),
            'id': self.vocab_context_entry.id,
            'vocab_entry_id': self.vocab_entry.id,
            'vocab_entry_url': drf_reverse(
                'api:vocab-entry-detail',
                kwargs={'pk': self.vocab_entry.id},
                request=self.request
            ),
            'vocab_entry': self.vocab_entry.entry,
            'vocab_context_url': drf_reverse(
                'api:vocab-context-detail',
                kwargs={'pk': self.vocab_context.id},
                request=self.request
            ),
            'vocab_context': self.vocab_context.content,
            'vocab_entry_tags': [self.vocab_tag.content],
            'date_created': self.vocab_context_entry.date_created.isoformat(),
            'date_updated': self.vocab_context_entry.date_updated.isoformat(),
        })
        json_data = self.serializer.json_data()
        self.assertEqual(json.loads(expected_json_data), json.loads(json_data))
