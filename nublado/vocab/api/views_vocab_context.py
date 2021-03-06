from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin,
    RetrieveModelMixin, UpdateModelMixin
)
from rest_framework.response import Response
from rest_framework.viewsets import (
    GenericViewSet
)

from django.db.models import Count

from core.api.views_api import APIDefaultsMixin
from core.utils import str_to_bool
from ..models import (
    VocabEntry, VocabContext, VocabContextAudio,
    VocabContextEntry, VocabSource
)
from ..serializers import (
    VocabContextSerializer, VocabContextAudioSerializer,
    VocabContextEntrySerializer
)
from .pagination import SmallPagination
from .permissions import (
    ReadPermission, SourceCreatorPermission,
    SourceContextCreatorPermission, SourceContextEntryCreatorPermission
)
from .views_mixins import BatchMixin


vocab_context_qs = VocabContext.objects.select_related(
    "vocab_source"
).prefetch_related(
    "vocabcontextentry_set__vocab_entry",
    "vocabcontextentry_set__vocab_entry_tags",
    "vocab_context_audios__creator"
)


class VocabContextViewSet(
    APIDefaultsMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    serializer_class = VocabContextSerializer
    queryset = vocab_context_qs
    permission_classes = [ReadPermission, SourceContextCreatorPermission]
    pagination_class = SmallPagination

    def get_queryset(self):
        qs = self.queryset.order_by("-date_created")

        return qs

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)

        return obj

    @action(methods=["post"], detail=True)
    def add_vocab_entry(self, request, pk=None):
        vocab_entry_id = request.data.get("vocab_entry_id", None)

        if not vocab_entry_id:
            raise ParseError("vocab_entry_id required")

        # Force permission check
        vocab_context = self.get_object()

        if not VocabContextEntry.objects.filter(vocab_entry_id=vocab_entry_id, vocab_context_id=pk).exists():
            VocabContextEntry.objects.create(vocab_entry_id=vocab_entry_id, vocab_context_id=pk)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=["post"], detail=True)
    def add_vocab_entry_tag(self, request, pk=None):
        vocab_entry_id = request.data.get("vocab_entry_id", None)

        if not vocab_entry_id:
            raise ParseError("vocab_entry_id required")

        vocab_entry_tag = request.data.get("vocab_entry_tag", None)

        if not vocab_entry_tag:
            raise ParseError("vocab_entry_tag required")

        # Force permission check
        vocab_context = self.get_object()

        vocab_entry_context = get_object_or_404(
            VocabContextEntry,
            vocab_entry_id=vocab_entry_id,
            vocab_context_id=pk
        )
        vocab_entry_context.add_vocab_entry_tag(vocab_entry_tag)

        return Response(status=status.HTTP_201_CREATED)

    @action(methods=["delete", "post"], detail=True)
    def remove_vocab_entry(self, request, pk=None):
        vocab_entry_id = request.data.get("vocab_entry_id", None)

        if not vocab_entry_id:
            raise ParseError("vocab_entry_id required")

        # Force permission check
        vocab_context = self.get_object()

        vocab_entry_context = get_object_or_404(
            VocabContextEntry,
            vocab_entry_id=vocab_entry_id,
            vocab_context_id=pk
        )
        vocab_entry_context.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["delete", "post"], detail=True)
    def remove_vocab_entry_tag(self, request, pk=None):
        vocab_entry_id = request.data.get("vocab_entry_id", None)

        if not vocab_entry_id:
            raise ParseError("vocab_entry_id required")

        vocab_entry_tag = request.data.get("vocab_entry_tag", None)

        if not vocab_entry_tag:
            raise ParseError("vocab_entry_tag required")

        # Force permission check
        vocab_context = self.get_object()

        vocab_entry_context = get_object_or_404(
            VocabContextEntry,
            vocab_entry_id=vocab_entry_id,
            vocab_context_id=pk
        )
        vocab_entry_context.remove_vocab_entry_tag(vocab_entry_tag)

        return Response(status=status.HTTP_204_NO_CONTENT)


class NestedVocabContextViewSet(
    APIDefaultsMixin, BatchMixin, CreateModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    queryset = vocab_context_qs
    serializer_class = VocabContextSerializer
    vocab_source = None
    permission_classes = [ReadPermission, SourceCreatorPermission]
    pagination_class = SmallPagination

    def get_vocab_source(self, vocab_source_pk=None):
        if not self.vocab_source:
            self.vocab_source = get_object_or_404(VocabSource, id=vocab_source_pk)

        return self.vocab_source

    def get_queryset(self):
        qs = self.queryset.filter(vocab_source_id=self.kwargs["vocab_source_pk"])

        filter_audios = self.request.query_params.get("filter_audios", None)
        if str_to_bool(filter_audios):
            # If filter_audios query_param, then only return contexts with audios.
            qs = qs.annotate(
                audio_count=Count("vocab_context_audios")
            ).filter(audio_count__gte=1)

        qs = qs.order_by("order")

        return qs

    def create(self, request, *args, **kwargs):
        self.get_vocab_source(vocab_source_pk=kwargs["vocab_source_pk"])
        self.check_object_permissions(request, self.vocab_source)

        return super(NestedVocabContextViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(vocab_source=self.vocab_source)

    def list(self, request, *args, **kwargs):
        self.get_vocab_source(vocab_source_pk=kwargs["vocab_source_pk"])

        return super(NestedVocabContextViewSet, self).list(request, *args, **kwargs)


vocab_context_entry_qs = VocabContextEntry.objects.select_related(
    "vocab_entry", "vocab_context", "vocab_context__vocab_source"
).prefetch_related(
    "vocab_entry_tags",
    "vocab_context__vocab_context_audios__creator"
)


class VocabContextEntryViewSet(
    APIDefaultsMixin, RetrieveModelMixin, DestroyModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    queryset = vocab_context_entry_qs
    serializer_class = VocabContextEntrySerializer
    permission_classes = [
        ReadPermission,
        SourceContextEntryCreatorPermission
    ]
    pagination_class = SmallPagination

    def get_queryset(self):
        vocab_entry_id = self.request.query_params.get("vocab_entry", None)
        vocab_source_id = self.request.query_params.get("vocab_source", None)

        if vocab_entry_id:
            self.queryset = self.queryset.filter(
                vocab_entry_id=vocab_entry_id
            )

        if vocab_source_id:
            self.queryset = self.queryset.filter(
                vocab_context__vocab_source_id=vocab_source_id
            )

        return self.queryset

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)

        return obj

    @action(methods=["get"], detail=False)
    def detail_data(self, request):
        """
        Retrieve VocabEntry object based on entry post data.
        """
        vocab_entry_id = request.query_params.get("vocab_entry", None)

        if not vocab_entry_id:
            raise ParseError("vocab_entry required")

        vocab_context_id = request.query_params.get("vocab_context", None)

        if not vocab_context_id:
            raise ParseError("vocab_context_id required")

        vocab_entry_context = get_object_or_404(
            VocabContextEntry,
            vocab_context_id=vocab_context_id,
            vocab_entry_id=vocab_entry_id
        )
        serializer = self.get_serializer(vocab_entry_context)

        return Response(
            status=status.HTTP_200_OK,
            data=serializer.data
        )


class NestedVocabContextEntryViewSet(
    APIDefaultsMixin, CreateModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    queryset = vocab_context_entry_qs
    serializer_class = VocabContextEntrySerializer
    vocab_entry = None
    vocab_context = None

    pagination_class = SmallPagination
    permission_classes = [ReadPermission, SourceContextCreatorPermission]

    def get_vocab_entry(self, vocab_entry_entry=None):
        if not self.vocab_entry:
            self.vocab_entry = get_object_or_404(VocabEntry, entry=vocab_entry_entry)

        return self.vocab_entry

    def get_vocab_context(self, vocab_context_pk=None):
        if not self.vocab_context:
            self.vocab_context = get_object_or_404(VocabContext, pk=vocab_context_pk)

        return self.vocab_context

    def get_queryset(self):
        return self.queryset.filter(vocab_context_id=self.kwargs["vocab_context_pk"])

    def create(self, request, *args, **kwargs):
        # Vocab entry text from request
        vocab_entry_entry = self.request.data.get("vocab_entry_entry", None)

        if not vocab_entry_entry:
            raise ParseError("vocab_entry_entry required")

        self.get_vocab_entry(vocab_entry_entry=vocab_entry_entry)
        self.get_vocab_context(
            vocab_context_pk=self.kwargs["vocab_context_pk"]
        )
        self.check_object_permissions(request, self.vocab_context)

        return super(NestedVocabContextEntryViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(
            vocab_entry=self.vocab_entry,
            vocab_context=self.vocab_context
        )

    def list(self, request, *args, **kwargs):
        self.get_vocab_context(vocab_context_pk=kwargs["vocab_context_pk"])

        return super(NestedVocabContextEntryViewSet, self).list(request, *args, **kwargs)


class VocabContextAudioViewSet(
    APIDefaultsMixin, RetrieveModelMixin, UpdateModelMixin,
    DestroyModelMixin, ListModelMixin, GenericViewSet
):
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    serializer_class = VocabContextAudioSerializer
    queryset = VocabContextAudio.objects.select_related(
        "vocab_context", "vocab_context__vocab_source", "creator"
    ).order_by("-date_created")
    permission_classes = [ReadPermission]
    pagination_class = SmallPagination

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj.post)
        return obj


class NestedVocabContextAudioViewSet(
    APIDefaultsMixin, CreateModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    queryset = VocabContextAudio.objects.select_related(
        "vocab_context", "vocab_context__vocab_source",
        "creator"
    ).order_by("-date_created")
    serializer_class = VocabContextAudioSerializer
    vocab_context = None
    permission_classes = [ReadPermission]
    pagination_class = SmallPagination

    def get_vocab_context(self, vocab_context_pk=None):
        if not self.vocab_context:
            self.vocab_context = get_object_or_404(
                VocabContext.objects.select_related("vocab_source"),
                id=vocab_context_pk
            )
        return self.vocab_context

    def get_queryset(self):
        return self.queryset.filter(vocab_context_id=self.kwargs["vocab_context_pk"])

    def create(self, request, *args, **kwargs):
        self.get_vocab_context(vocab_context_pk=kwargs["vocab_context_pk"])
        return super(NestedVocabContextAudioViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(
            creator=self.request.user,
            vocab_context=self.vocab_context
        )

    def list(self, request, *args, **kwargs):
        self.get_vocab_context(vocab_context_pk=kwargs["vocab_context_pk"])
        no_pagination = self.request.query_params.get("no_pagination", None)
        if str_to_bool(no_pagination):
            self.pagination_class = None
        return super(NestedVocabContextAudioViewSet, self).list(request, *args, **kwargs)
