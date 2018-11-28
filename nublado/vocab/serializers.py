from rest_framework.serializers import (
    HyperlinkedIdentityField, HyperlinkedRelatedField, HyperlinkedModelSerializer,
    ListSerializer, ReadOnlyField, StringRelatedField
)

from django.contrib.auth import get_user_model

from core.serializers import BaseSerializer, UUIDEncoder
from .models import (
    VocabEntry, VocabContextEntry, VocabContext,
    VocabProject, VocabSource
)

User = get_user_model()


class VocabEntryListSerializer(ListSerializer):
    pass


class VocabProjectSerializer(BaseSerializer, HyperlinkedModelSerializer):
    json_encoder = UUIDEncoder
    minimal_data_fields = [
        'name', 'description', 'date_created'
    ]
    url = HyperlinkedIdentityField(
        view_name='api:vocab-project-detail',
        lookup_field='slug'
    )
    owner_id = ReadOnlyField(source='owner.id')
    owner_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='api:user-detail',
        lookup_field='username',
        source='owner'
    )
    vocab_sources_url = HyperlinkedIdentityField(
        view_name='api:nested-vocab-source-list',
        lookup_url_kwarg='vocab_project_slug',
        lookup_field='slug'
    )

    class Meta:
        list_serializer = VocabEntryListSerializer
        model = VocabProject
        fields = (
            'url', 'id', 'owner_id', 'owner_url', 'vocab_sources_url',
            'name', 'description', 'slug', 'date_created', 'date_updated',
        )
        read_only_fields = (
            'url', 'id', 'owner_id', 'owner_url', 'vocab_sources_url',
            'slug', 'date_created', 'date_updated'
        )

    def create(self, validated_data):
        return VocabProject.objects.create(**validated_data)


class VocabEntrySerializer(BaseSerializer, HyperlinkedModelSerializer):
    json_encoder = UUIDEncoder
    minimal_data_fields = [
        'language', 'entry', 'pronunciation_spelling',
        'pronunciation_ipa', 'description', 'date_created'
    ]
    url = HyperlinkedIdentityField(
        view_name='api:vocab-entry-detail',
        lookup_field='slug'
    )

    class Meta:
        list_serializer = VocabEntryListSerializer
        model = VocabEntry
        fields = (
            'url', 'id', 'language',
            'entry', 'pronunciation_spelling',
            'pronunciation_ipa', 'description',
            'slug', 'date_created', 'date_updated',
        )
        read_only_fields = (
            'url', 'id', 'slug', 'date_created', 'date_updated'
        )

    def create(self, validated_data):
        return VocabEntry.objects.create(**validated_data)


class VocabDefinitionSerializer(BaseSerializer, HyperlinkedModelSerializer):
    pass


class VocabWebReferenceSerializer(BaseSerializer, HyperlinkedModelSerializer):
    pass


class VocabSourceListSerializer(ListSerializer):
    pass


class VocabSourceSerializer(BaseSerializer, HyperlinkedModelSerializer):
    json_encoder = UUIDEncoder
    minimal_data_fields = [
        'source_type', 'name',
        'description', 'date_created'
    ]
    url = HyperlinkedIdentityField(
        view_name='api:vocab-source-detail',
        lookup_field='slug'
    )
    project_id = ReadOnlyField(source='vocab_project.id')
    project_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='api:vocab-project-detail',
        lookup_field='slug',
        source='vocab_project'
    )
    creator_id = ReadOnlyField(source='creator.id')
    creator_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='api:user-detail',
        lookup_field='username',
        source='creator'
    )
    vocab_contexts_url = HyperlinkedIdentityField(
        view_name='api:nested-vocab-context-list',
        lookup_url_kwarg='vocab_source_slug',
        lookup_field='slug'
    )

    class Meta:
        list_serializer = VocabSourceListSerializer
        model = VocabSource
        fields = (
            'url', 'id', 'project_id', 'project_url', 'creator_id', 'creator_url',
            'name', 'description', 'source_type', 'slug', 'vocab_contexts_url',
            'date_created', 'date_updated'
        )
        read_only_fields = (
            'url', 'id', 'project_id', 'project_url', 'creator_id', 'creator_url',
            'slug', 'vocab_contexts_url', 'date_created', 'date_updated'
        )

    def create(self, validated_data):
        return VocabSource.objects.create(**validated_data)


class VocabContextSerializer(BaseSerializer, HyperlinkedModelSerializer):
    json_encoder = UUIDEncoder
    minimal_data_fields = ['content', 'date_created']
    url = HyperlinkedIdentityField(
        view_name='api:vocab-context-detail',
        lookup_field='pk'
    )
    vocab_source_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='api:vocab-source-detail',
        lookup_field='slug',
        source='vocab_source'
    )
    vocab_entries_url = HyperlinkedIdentityField(
        view_name='api:nested-vocab-context-entry-list',
        lookup_url_kwarg='vocab_context_pk'
    )

    class Meta:
        model = VocabContext
        fields = (
            'url', 'id', 'vocab_source_url',
            'vocab_source_id', 'content', 'vocab_entries_url',
            'date_created', 'date_updated',
        )
        read_only_fields = (
            'url', 'id', 'vocab_source_url',
            'vocab_source_id', 'vocab_entries_url', 'date_created', 'date_updated'
        )

    def create(self, validated_data):
        return VocabContext.objects.create(**validated_data)


class VocabContextEntrySerializer(BaseSerializer, HyperlinkedModelSerializer):
    minimal_data_fields = [
        'vocab_entry', 'vocab_context', 'vocab_entry_tags',
        'date_created'
    ]
    url = HyperlinkedIdentityField(
        view_name='api:vocab-context-entry-detail',
        lookup_field='pk'
    )
    vocab_entry_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='api:vocab-entry-detail',
        lookup_field='slug',
        source='vocab_entry'
    )
    vocab_entry = StringRelatedField(many=False)
    vocab_context_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='api:vocab-context-detail',
        lookup_field='pk',
        source='vocab_context'
    )
    vocab_context = StringRelatedField(many=False)
    vocab_entry_tags = StringRelatedField(many=True)

    class Meta:
        model = VocabContextEntry
        fields = (
            'url', 'id', 'vocab_entry_url', 'vocab_entry_id', 'vocab_entry', 'vocab_context_url',
            'vocab_context', 'date_created', 'date_updated', 'vocab_entry_tags'
        )
        read_only_fields = (
            'url', 'id', 'vocab_entry_url', 'vocab_entry_id', 'vocab_context_url',
            'date_created', 'date_updated'
        )
