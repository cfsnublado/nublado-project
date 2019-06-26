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

from core.api.views_api import APIDefaultsMixin
from ..models import (
    VocabEntry, VocabContextEntry,
    VocabContext, VocabSource
)
from ..serializers import (
    VocabContextEntrySerializer, VocabContextSerializer
)
from .pagination import SmallPagination
from .permissions import (
    ReadPermission, ReadWritePermission, SourceContextCreatorPermission
)
from .views_mixins import BatchMixin


class VocabContextViewSet(
    APIDefaultsMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    serializer_class = VocabContextSerializer
    queryset = VocabContext.objects.select_related('vocab_source')
    permission_classes = [ReadPermission, SourceContextCreatorPermission]
    pagination_class = SmallPagination

    def get_queryset(self):
        qs = self.queryset.prefetch_related(
            'vocabcontextentry_set__vocab_entry',
            'vocabcontextentry_set__vocab_entry_tags'
        )

        return qs

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)

        return obj

    @action(methods=['post'], detail=True)
    def add_vocab_entry(self, request, pk=None):
        vocab_entry_id = request.data.get('vocab_entry_id', None)

        if not vocab_entry_id:
            raise ParseError('vocab_entry_id required')

        # Force permission check
        vocab_context = self.get_object()

        if not VocabContextEntry.objects.filter(vocab_entry_id=vocab_entry_id, vocab_context_id=pk).exists():
            VocabContextEntry.objects.create(vocab_entry_id=vocab_entry_id, vocab_context_id=pk)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=True)
    def add_vocab_entry_tag(self, request, pk=None):
        vocab_entry_id = request.data.get('vocab_entry_id', None)

        if not vocab_entry_id:
            raise ParseError('vocab_entry_id required')

        vocab_entry_tag = request.data.get('vocab_entry_tag', None)

        if not vocab_entry_tag:
            raise ParseError('vocab_entry_tag required')

        # Force permission check
        vocab_context = self.get_object()

        vocab_entry_context = get_object_or_404(
            VocabContextEntry,
            vocab_entry_id=vocab_entry_id,
            vocab_context_id=pk
        )
        vocab_entry_context.add_vocab_entry_tag(vocab_entry_tag)

        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['delete', 'post'], detail=True)
    def remove_vocab_entry(self, request, pk=None):
        vocab_entry_id = request.data.get('vocab_entry_id', None)

        if not vocab_entry_id:
            raise ParseError('vocab_entry_id required')

        # Force permission check
        vocab_context = self.get_object()

        vocab_entry_context = get_object_or_404(
            VocabContextEntry,
            vocab_entry_id=vocab_entry_id,
            vocab_context_id=pk
        )
        vocab_entry_context.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['delete', 'post'], detail=True)
    def remove_vocab_entry_tag(self, request, pk=None):
        vocab_entry_id = request.data.get('vocab_entry_id', None)

        if not vocab_entry_id:
            raise ParseError('vocab_entry_id required')

        vocab_entry_tag = request.data.get('vocab_entry_tag', None)

        if not vocab_entry_tag:
            raise ParseError('vocab_entry_tag required')

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
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    queryset = VocabContext.objects.select_related('vocab_source')
    serializer_class = VocabContextSerializer
    vocab_source = None
    permission_classes = [ReadWritePermission]
    pagination_class = SmallPagination

    def get_vocab_source(self, vocab_source_pk=None):
        if not self.vocab_source:
            self.vocab_source = get_object_or_404(VocabSource, id=vocab_source_pk)

        return self.vocab_source

    def create(self, request, *args, **kwargs):
        vocab_source = self.get_vocab_source(vocab_source_pk=kwargs['vocab_source_pk'])
        self.check_object_permissions(request, vocab_source)

        return super(NestedVocabContextViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        vocab_source = self.get_vocab_source(vocab_source_pk=self.kwargs['vocab_source_pk'])
        serializer.save(vocab_source=vocab_source)

    def get_queryset(self):
        qs = self.queryset.prefetch_related(
            'vocabcontextentry_set__vocab_entry',
            'vocabcontextentry_set__vocab_entry_tags'
        )
        qs = qs.filter(vocab_source_id=self.kwargs['vocab_source_pk'])
        return qs

    def list(self, request, *args, **kwargs):
        self.get_vocab_source(vocab_source_pk=kwargs['vocab_source_pk'])

        return super(NestedVocabContextViewSet, self).list(request, *args, **kwargs)


class VocabContextEntryViewSet(
    APIDefaultsMixin, RetrieveModelMixin, DestroyModelMixin,
    ListModelMixin, GenericViewSet
):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    queryset = VocabContextEntry.objects.select_related(
        'vocab_entry', 'vocab_context', 'vocab_context__vocab_source'
    ).prefetch_related(
        'vocab_entry_tags'
    )
    serializer_class = VocabContextEntrySerializer
    permission_classes = [ReadWritePermission]
    pagination_class = SmallPagination

    def get_queryset(self):
        vocab_entry_id = self.request.query_params.get('vocab_entry', None)
        vocab_source_id = self.request.query_params.get('vocab_source', None)

        if vocab_entry_id:
            self.queryset = self.queryset.filter(
                vocab_entry_id=vocab_entry_id
            )

        if vocab_source_id:
            self.queryset = self.queryset.filter(
                vocab_context__vocab_source_id=vocab_source_id
            )

        return self.queryset

    @action(methods=['get'], detail=False)
    def detail_data(self, request):
        '''
        Retrieve VocabEntry object based on entry post data.
        '''
        vocab_entry_id = request.query_params.get('vocab_entry', None)

        if not vocab_entry_id:
            raise ParseError('vocab_entry required')

        vocab_context_id = request.query_params.get('vocab_context', None)

        if not vocab_context_id:
            raise ParseError('vocab_context_id required')

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


class NestedVocabContextEntryViewSet(APIDefaultsMixin, CreateModelMixin, ListModelMixin, GenericViewSet):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    queryset = VocabContextEntry.objects.select_related(
        'vocab_entry', 'vocab_context', 'vocab_context__vocab_source'
    ).prefetch_related(
        'vocab_entry_tags'
    )
    serializer_class = VocabContextEntrySerializer
    vocab_entry = None
    vocab_context = None

    def get_vocab_entry(self, vocab_entry_entry=None):
        if not self.vocab_entry:
            self.vocab_entry = get_object_or_404(VocabEntry, entry=vocab_entry_entry)

        return self.vocab_entry

    def get_vocab_context(self, vocab_context_pk=None):
        if not self.vocab_context:
            self.vocab_context = get_object_or_404(VocabContext, pk=vocab_context_pk)

        return self.vocab_context

    def get_queryset(self):
        return self.queryset.filter(vocab_context_id=self.kwargs['vocab_context_pk'])

    def perform_create(self, serializer):
        # Vocab entry text from request
        vocab_entry_entry = self.request.data.get('vocab_entry_entry', None)

        if not vocab_entry_entry:
            raise ParseError('vocab_entry_entry required')

        vocab_entry = self.get_vocab_entry(vocab_entry_entry=vocab_entry_entry)
        vocab_context = self.get_vocab_context(vocab_context_pk=self.kwargs['vocab_context_pk'])
        serializer.save(vocab_entry=vocab_entry, vocab_context=vocab_context)

    def list(self, request, *args, **kwargs):
        self.get_vocab_context(vocab_context_pk=kwargs['vocab_context_pk'])

        return super(NestedVocabContextEntryViewSet, self).list(request, *args, **kwargs)
