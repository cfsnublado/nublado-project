from rest_framework.serializers import (
    HyperlinkedIdentityField, HyperlinkedRelatedField, HyperlinkedModelSerializer,
    ListSerializer, ReadOnlyField, SerializerMethodField, StringRelatedField
)

from django.contrib.auth import get_user_model

from core.serializers import BaseSerializer, UUIDEncoder
from .models import (
    VocabDefinition, VocabEntry, VocabContextEntry,
    VocabContext, VocabProject, VocabSource
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
        lookup_field='pk'
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
        lookup_url_kwarg='vocab_project_pk',
        lookup_field='pk'
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
        lookup_field='pk'
    )
    vocab_definitions_url = HyperlinkedIdentityField(
        view_name='api:nested-vocab-definition-list',
        lookup_url_kwarg='vocab_entry_pk',
        lookup_field='pk'
    )

    class Meta:
        list_serializer = VocabEntryListSerializer
        model = VocabEntry
        fields = (
            'url', 'id', 'language',
            'entry', 'pronunciation_spelling',
            'pronunciation_ipa', 'description',
            'slug', 'vocab_definitions_url',
            'date_created', 'date_updated',
        )
        read_only_fields = (
            'url', 'id', 'slug', 'vocab_definitions_url',
            'date_created', 'date_updated'
        )

    def create(self, validated_data):
        return VocabEntry.objects.create(**validated_data)


class VocabDefinitionSerializer(BaseSerializer, HyperlinkedModelSerializer):
    json_encoder = UUIDEncoder
    minimal_data_fields = [
        'definition', 'definition_type',
        'date_created'
    ]
    url = HyperlinkedIdentityField(
        view_name='api:vocab-definition-detail',
        lookup_field='pk'
    )
    vocab_entry_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='api:vocab-entry-detail',
        lookup_field='pk',
        source='vocab_entry'
    )
    definition_type_name = SerializerMethodField()

    def get_definition_type_name(self, obj):
        return obj.get_definition_type_display()

    class Meta:
        model = VocabDefinition
        fields = (
            'url', 'id', 'vocab_entry_url',
            'vocab_entry_id', 'definition', 'definition_type',
            'definition_type_name', 'date_created', 'date_updated',
        )
        read_only_fields = (
            'url', 'id', 'vocab_entry_url',
            'vocab_entry_id', 'date_created', 'date_updated'
        )


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
        lookup_field='pk'
    )
    project_id = ReadOnlyField(source='vocab_project.id')
    project_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='api:vocab-project-detail',
        lookup_field='pk',
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
        lookup_url_kwarg='vocab_source_pk',
        lookup_field='pk'
    )
    source_type_name = SerializerMethodField()

    def get_source_type_name(self, obj):
        return obj.get_source_type_display()

    class Meta:
        list_serializer = VocabSourceListSerializer
        model = VocabSource
        fields = (
            'url', 'id', 'project_id', 'project_url', 'creator_id', 'creator_url',
            'name', 'description', 'source_type', 'source_type_name',
            'slug', 'vocab_contexts_url', 'date_created', 'date_updated'
        )
        read_only_fields = (
            'url', 'id', 'project_id', 'project_url', 'creator_id', 'creator_url',
            'slug', 'vocab_contexts_url', 'source_type_name', 'date_created', 'date_updated'
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
        lookup_field='pk',
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
        lookup_field='pk',
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
