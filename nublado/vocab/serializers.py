from rest_framework.serializers import (
    CharField, HyperlinkedIdentityField, HyperlinkedRelatedField,
    HyperlinkedModelSerializer,
    IntegerField, ListSerializer, ReadOnlyField, Serializer,
    SerializerMethodField, StringRelatedField, PrimaryKeyRelatedField
)

from django.contrib.auth import get_user_model
from django.db import models

from core.serializers import (
    BaseSerializer, UUIDEncoder
)
from .models import (
    VocabEntry, VocabContextEntry,
    VocabContext, VocabContextAudio,
    VocabSource
)

User = get_user_model()


class VocabSourceEntrySerializer(Serializer):
    id = IntegerField()
    vocab_source_id = IntegerField()
    language = CharField()
    entry = CharField()
    slug = CharField()


class VocabEntryListSerializer(ListSerializer):
    pass


class VocabEntrySerializer(BaseSerializer, HyperlinkedModelSerializer):
    json_encoder = UUIDEncoder
    minimal_data_fields = [
        "language", "entry", "description", "date_created"
    ]
    url = HyperlinkedIdentityField(
        view_name="api:vocab-entry-detail",
        lookup_field="pk"
    )

    class Meta:
        list_serializer_class = VocabEntryListSerializer
        model = VocabEntry
        fields = (
            "url", "id", "language",
            "entry", "description",
            "slug", "date_created", "date_updated",
        )
        read_only_fields = (
            "url", "id", "slug",
            "date_created", "date_updated"
        )

    def create(self, validated_data):
        return VocabEntry.objects.create(**validated_data)


class VocabSourceListSerializer(ListSerializer):
    pass


class VocabSourceSerializer(BaseSerializer, HyperlinkedModelSerializer):
    json_encoder = UUIDEncoder
    minimal_data_fields = [
        "source_type", "name",
        "description", "date_created"
    ]
    url = HyperlinkedIdentityField(
        view_name="api:vocab-source-detail",
        lookup_field="pk"
    )
    creator_id = ReadOnlyField(source="creator.id")
    creator_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="api:user-detail",
        lookup_field="username",
        source="creator"
    )
    vocab_contexts_url = HyperlinkedIdentityField(
        view_name="api:nested-vocab-context-list",
        lookup_url_kwarg="vocab_source_pk",
        lookup_field="pk"
    )
    source_type_name = SerializerMethodField()

    def get_source_type_name(self, obj):
        return obj.get_source_type_display()

    class Meta:
        list_serializer_class = VocabSourceListSerializer
        model = VocabSource
        fields = (
            "url", "id", "creator_id", "creator_url",
            "name", "description", "source_type", "source_type_name",
            "slug", "vocab_contexts_url",
            "date_created", "date_updated"
        )
        read_only_fields = (
            "url", "id", "creator_id", "creator_url",
            "slug", "vocab_contexts_url",
            "source_type_name", "date_created", "date_updated"
        )

    def create(self, validated_data):
        return VocabSource.objects.create(**validated_data)


class VocabContextAudioListSerializer(
    ListSerializer
):
    pass


class VocabContextAudioSerializer(
    BaseSerializer,
    HyperlinkedModelSerializer
):
    json_encoder = UUIDEncoder
    minimal_data_fields = [
        "name", "audio_url"
    ]
    url = HyperlinkedIdentityField(
        view_name="api:vocab-context-audio-detail",
        lookup_field="pk"
    )
    vocab_context_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="api:vocab-context-detail",
        lookup_field="pk",
        source="vocab_context"
    )
    creator_id = ReadOnlyField(source="creator.id")
    creator_username = ReadOnlyField(source="creator.username")
    creator_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="api:user-detail",
        lookup_field="username",
        source="creator"
    )

    class Meta:
        list_serializer_class = VocabContextAudioListSerializer
        model = VocabContextAudio
        fields = (
            "url", "id", "vocab_context_url", "creator_id", "creator_username",
            "creator_url", "name", "audio_url", "slug",
            "date_created", "date_updated"
        )
        read_only_fields = (
            "url", "id", "vocab_context_url",
            "creator_id", "creator_url", "slug",
            "date_created", "date_updated"
        )

    def create(self, validated_data):
        return VocabContextAudio.objects.create(**validated_data)


class VocabContextSerializer(BaseSerializer, HyperlinkedModelSerializer):
    json_encoder = UUIDEncoder
    minimal_data_fields = ["order", "content", "date_created"]

    url = HyperlinkedIdentityField(
        view_name="api:vocab-context-detail",
        lookup_field="pk"
    )
    vocab_source_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="api:vocab-source-detail",
        lookup_field="pk",
        source="vocab_source"
    )
    vocab_source_name = StringRelatedField(
        many=False,
        source="vocab_source"
    )
    vocab_entries_url = HyperlinkedIdentityField(
        view_name="api:nested-vocab-context-entry-list",
        lookup_url_kwarg="vocab_context_pk"
    )
    vocab_entry_tags = SerializerMethodField()

    def get_vocab_entry_tags(self, obj):
        return obj.get_entries_and_tags()

    vocab_context_audios_url = HyperlinkedIdentityField(
        view_name="api:nested-vocab-context-audio-list",
        lookup_url_kwarg="vocab_context_pk",
        lookup_field="pk"
    )
    # vocab_context_audios = PrimaryKeyRelatedField(queryset=VocabContextAudio.objects.all(), many=True)
    vocab_context_audios = VocabContextAudioSerializer(many=True, read_only=True)

    class Meta:
        model = VocabContext
        fields = (
            "url", "id", "vocab_source_url",
            "vocab_source_id", "vocab_source_name", "content", "order", "vocab_entries_url",
            "vocab_entry_tags", "vocab_context_audios_url", "vocab_context_audios",
            "date_created", "date_updated",
        )
        read_only_fields = (
            "url", "id", "vocab_source_name", "vocab_source_url",
            "vocab_source_id", "order", "vocab_entries_url", "vocab_entry_tags",
            "vocab_context_audios_url", "vocab_context_audios",
            "date_created", "date_updated"
        )

    def create(self, validated_data):
        return VocabContext.objects.create(**validated_data)

    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response["vocab_context_audios"] = VocabContextAudioSerializer(
    #         instance.vocab_context_audios.all(),
    #         context=self.context,
    #         many=True
    #     ).data
    #     return response


class VocabContextEntrySerializer(BaseSerializer, HyperlinkedModelSerializer):
    minimal_data_fields = [
        "vocab_entry", "vocab_context", "vocab_entry_tags",
        "date_created"
    ]
    url = HyperlinkedIdentityField(
        view_name="api:vocab-context-entry-detail",
        lookup_field="pk"
    )
    vocab_entry_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="api:vocab-entry-detail",
        lookup_field="pk",
        source="vocab_entry"
    )
    vocab_entry = StringRelatedField(many=False)
    vocab_context_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="api:vocab-context-detail",
        lookup_field="pk",
        source="vocab_context"
    )
    vocab_context = StringRelatedField(many=False)
    vocab_source_id = ReadOnlyField(source="vocab_context.vocab_source_id")
    vocab_source_url = HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="api:vocab-source-detail",
        lookup_field="pk",
        source="vocab_context.vocab_source"
    )
    vocab_source = StringRelatedField(
        many=False,
        source="vocab_context.vocab_source"
    )
    vocab_source_slug = StringRelatedField(
        many=False,
        source="vocab_context.vocab_source.slug"
    )
    vocab_entry_tags = StringRelatedField(many=True)

    class Meta:
        model = VocabContextEntry
        fields = (
            "url", "id", "vocab_entry_url", "vocab_entry_id", "vocab_entry",
            "vocab_context_id", "vocab_context_url",
            "vocab_context", "vocab_source_id", "vocab_source_url", "vocab_source",
            "vocab_source_slug", "date_created",
            "date_updated", "vocab_entry_tags"
        )
        read_only_fields = (
            "url", "id", "vocab_entry_url", "vocab_entry_id", "vocab_context_id",
            "vocab_context_url", "vocab_source_id", "vocab_source_url",
            "vocab_source", "vocab_source_slug", "date_created", "date_updated"
        )
